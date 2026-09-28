"""Roslyn compile check for a Unity project, without opening Unity or running tests.

Builds only the Unity-generated .csproj files that contain the changed C# files,
with `dotnet build` (Roslyn). Project references are replaced by the assemblies
Unity already compiled into Library/ScriptAssemblies, so no dependency is rebuilt.
New files are injected and deleted files removed, so the result does not depend
on Unity having regenerated the project files yet.

Exit codes: 0 COMPILE_OK, 1 COMPILE_ERRORS, 2 COMPILE_UNVERIFIED, 3 usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from xml.sax.saxutils import quoteattr

EXIT_OK = 0
EXIT_ERRORS = 1
EXIT_UNVERIFIED = 2
EXIT_USAGE = 3
MAX_REPORTED_ERRORS = 40
FIRSTPASS_ROOTS = ("assets/plugins/", "assets/standard assets/", "assets/pro standard assets/")
ERROR_PATTERN = re.compile(r"\berror (?P<code>[A-Z]+\d+):")
PROJECT_SUFFIX = re.compile(r"\s+\[[^\]]+\.csproj\]$")


class UnverifiedError(Exception):
    """The check cannot give a trustworthy answer; fall back to a Unity compile."""


def normalize(path: Path | str) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def msbuild_escape(text: str) -> str:
    return "".join(f"%{ord(character):02X}" if character in "%;$@'" else character for character in text)


class CsProject:
    """The parts of one generated .csproj that the check needs."""

    def __init__(self, path: Path) -> None:
        self.path = path
        root = ElementTree.parse(path).getroot()
        directory = path.parent
        self.assembly = self._property(root, "AssemblyName") or path.stem
        self.compile_items: dict[str, str] = {}
        for item in root.iterfind(".//{*}Compile"):
            include = item.get("Include")
            if include:
                self.compile_items[normalize(directory / include.replace("\\", "/"))] = include
        self.references = [
            normalize(directory / item.get("Include").replace("\\", "/"))
            for item in root.iterfind(".//{*}ProjectReference")
            if item.get("Include")
        ]
        hint_paths = [element.text.strip() for element in root.iterfind(".//{*}HintPath") if element.text]
        analyzers = [item.get("Include") for item in root.iterfind(".//{*}Analyzer") if item.get("Include")]
        self.external_files = [directory / value.replace("\\", "/") for value in hint_paths + analyzers]
        self.is_sdk_style = root.get("Sdk") is not None or any(
            item.get("Sdk") for item in root.iterfind(".//{*}Import")
        )
        output_path = (self._property(root, "OutputPath") or "Temp/bin/Debug/").replace("\\", "/")
        self.output_file = directory / output_path / f"{self.assembly}.dll"
        intermediate = self._property(root, "BaseIntermediateOutputPath") or "obj/"
        intermediate = intermediate.replace("$(MSBuildProjectName)", path.stem).replace("\\", "/")
        self.restore_marker = directory / intermediate / "project.assets.json"

    @staticmethod
    def _property(root: ElementTree.Element, name: str) -> str | None:
        element = root.find(f".//{{*}}{name}")
        return element.text.strip() if element is not None and element.text else None

    def missing_external_files(self) -> list[Path]:
        return [path for path in dict.fromkeys(self.external_files) if not path.exists()]

    def newest_source_time(self) -> float:
        times = (os.stat(item).st_mtime for item in self.compile_items if os.path.exists(item))
        return max(times, default=0.0)


class UnityProject:
    """Index of the generated .csproj files whose assemblies Unity currently compiles."""

    def __init__(self, root: Path) -> None:
        version_file = root / "ProjectSettings" / "ProjectVersion.txt"
        if not version_file.is_file():
            raise ValueError(f"{root} is not a Unity project (ProjectSettings/ProjectVersion.txt is missing).")
        self.root = root
        match = re.search(r"m_EditorVersion:\s*(\S+)", version_file.read_text(encoding="utf-8", errors="ignore"))
        self.version = match.group(1) if match else "unknown"
        self.script_assemblies = root / "Library" / "ScriptAssemblies"
        compiled = {path.stem.lower() for path in self.script_assemblies.glob("*.dll")}
        if not compiled:
            raise UnverifiedError(
                "Library/ScriptAssemblies is empty, so Unity has not compiled this project on this machine. "
                "Open it in Unity once, then run the check again."
            )
        generated = [CsProject(path) for path in sorted(root.glob("*.csproj"))]
        if not generated:
            raise UnverifiedError(
                "No generated .csproj files. Regenerate project files from the Unity Editor "
                "(Preferences > External Tools) and run the check again."
            )
        # Unity never deletes .csproj files of removed assemblies; only compiled assemblies are current.
        current = [project for project in generated if project.assembly.lower() in compiled]
        self.stale_count = len(generated) - len(current)
        self.projects = {normalize(project.path): project for project in current}
        self.by_assembly = {project.assembly.lower(): project for project in current}
        self.owners: dict[str, CsProject] = {}
        for project in sorted(current, key=lambda item: item.path.stat().st_mtime):
            for item in project.compile_items:
                self.owners[item] = project

    def plan(self, files: list[str]):
        """Map changed files to the projects that compile them."""
        affected: dict[str, CsProject] = {}
        additions: dict[str, list[str]] = {}
        removals: dict[str, list[str]] = {}
        notes: list[str] = []
        for raw in files:
            file_path = Path(os.path.abspath(raw if os.path.isabs(raw) else self.root / raw))
            suffix = file_path.suffix.lower()
            if suffix in (".asmdef", ".asmref"):
                raise UnverifiedError(
                    f"{file_path.name} changed. The generated projects stay stale until Unity regenerates them."
                )
            if suffix != ".cs":
                continue
            key = normalize(file_path)
            owner = self.owners.get(key)
            if owner is not None:
                affected[normalize(owner.path)] = owner
                if not file_path.exists():
                    removals.setdefault(normalize(owner.path), []).append(owner.compile_items[key])
                continue
            if not file_path.exists():
                notes.append(f"{raw}: deleted and not in any generated project")
                continue
            assembly = self.assembly_for_new_file(file_path)
            if assembly is None:
                notes.append(f"{raw}: in a hidden or ~ folder that Unity ignores")
                continue
            project = self.by_assembly.get(assembly.lower())
            if project is None:
                raise UnverifiedError(
                    f"Assembly {assembly} has no generated .csproj yet. Regenerate project files from Unity."
                )
            affected[normalize(project.path)] = project
            additions.setdefault(normalize(project.path), []).append(str(file_path))
        return list(affected.values()), additions, removals, notes

    def assembly_for_new_file(self, file_path: Path) -> str | None:
        """Return the assembly Unity compiles a not-yet-listed file into, or None if Unity ignores it."""
        relative = file_path.relative_to(self.root).as_posix()
        lowered = relative.lower()
        folders = relative.split("/")[:-1]
        if any(folder.startswith(".") or folder.endswith("~") for folder in folders):
            return None
        if lowered.startswith("assets/"):
            boundary = self.root / "Assets"
        elif lowered.startswith("packages/") and len(folders) >= 2:
            boundary = self.root / folders[0] / folders[1]
        else:
            raise UnverifiedError(f"{relative} is outside Assets/ and Packages/.")
        directory = file_path.parent
        while True:
            assembly = self._assembly_defined_in(directory)
            if assembly:
                return assembly
            if directory == boundary or directory == self.root:
                break
            directory = directory.parent
        if lowered.startswith("packages/"):
            raise UnverifiedError(f"{relative} is in a package without an assembly definition.")
        editor = "-Editor" if any(folder.lower() == "editor" for folder in folders) else ""
        firstpass = "-firstpass" if lowered.startswith(FIRSTPASS_ROOTS) else ""
        return f"Assembly-CSharp{editor}{firstpass}"

    def _assembly_defined_in(self, directory: Path) -> str | None:
        for asmdef in sorted(directory.glob("*.asmdef")):
            return read_json(asmdef).get("name")
        for asmref in sorted(directory.glob("*.asmref")):
            return self._resolve_reference(read_json(asmref).get("reference", ""), asmref)
        return None

    def _resolve_reference(self, reference: str, asmref: Path) -> str:
        if not reference.startswith("GUID:"):
            return reference
        guid = reference[5:].lower()
        metas = itertools.chain(self.root.glob("Assets/**/*.asmdef.meta"), self.root.glob("Packages/**/*.asmdef.meta"))
        for meta in metas:
            if f"guid: {guid}" in meta.read_text(encoding="utf-8", errors="ignore"):
                return read_json(meta.with_suffix("")).get("name")
        raise UnverifiedError(f"Cannot resolve {reference} from {asmref.name}.")

    def with_dependents(self, projects: list[CsProject]) -> list[CsProject]:
        """Add every current project that references the given ones, directly or transitively."""
        dependents: dict[str, list[str]] = {}
        for key, project in self.projects.items():
            for reference in project.references:
                dependents.setdefault(reference, []).append(key)
        selected = {normalize(project.path): project for project in projects}
        pending = list(selected)
        while pending:
            for dependent in dependents.get(pending.pop(), []):
                if dependent not in selected:
                    selected[dependent] = self.projects[dependent]
                    pending.append(dependent)
        return list(selected.values())

    def stale_dependencies(self, projects: list[CsProject]) -> list[CsProject]:
        """Referenced projects whose compiled assembly is older than their sources, plus every
        project between them and the given ones. Unity has not recompiled these yet."""
        closure: dict[str, CsProject] = {}
        pending = [normalize(project.path) for project in projects]
        while pending:
            key = pending.pop()
            if key in closure or key not in self.projects:
                continue
            closure[key] = self.projects[key]
            pending.extend(closure[key].references)
        stale: dict[str, bool] = {}

        def is_stale(key: str) -> bool:
            if key not in stale:
                stale[key] = False
                project = closure[key]
                compiled = self.script_assemblies / f"{project.assembly}.dll"
                own = not compiled.exists() or project.newest_source_time() > compiled.stat().st_mtime
                stale[key] = own or any(is_stale(reference) for reference in project.references if reference in closure)
            return stale[key]

        requested = {normalize(project.path) for project in projects}
        return [closure[key] for key in closure if key not in requested and is_stale(key)]

    def build_order(self, projects: list[CsProject]) -> list[CsProject]:
        """Dependencies first, so a dependent compiles against the fresh output of what it references."""
        wanted = {normalize(project.path) for project in projects}
        ordered: list[CsProject] = []
        visited: set[str] = set()

        def visit(project: CsProject) -> None:
            key = normalize(project.path)
            if key in visited:
                return
            visited.add(key)
            for reference in project.references:
                if reference in wanted:
                    visit(self.projects[reference])
            ordered.append(project)

        for project in sorted(projects, key=lambda item: item.assembly.lower()):
            visit(project)
        return ordered

    def write_build_targets(self, ordered: list[CsProject], additions, removals) -> Path:
        """Write an MSBuild file that, per built project, swaps project references for compiled
        assemblies and adds new or removes deleted sources."""
        built = {normalize(project.path) for project in ordered}
        groups = []
        for project in ordered:
            key = normalize(project.path)
            items = ["    <ProjectReference Remove=\"@(ProjectReference)\" />"]
            for reference in project.references:
                dependency = self.projects.get(reference)
                if dependency is None:
                    raise UnverifiedError(f"{project.assembly} references {Path(reference).name}, which Unity does not compile.")
                if reference in built:
                    assembly_file = dependency.output_file
                else:
                    assembly_file = self.script_assemblies / f"{dependency.assembly}.dll"
                    if not assembly_file.exists():
                        raise UnverifiedError(f"{assembly_file.name} is missing from Library/ScriptAssemblies.")
                items.append(
                    f"    <Reference Include={quoteattr(dependency.assembly)}>"
                    f"<HintPath>{msbuild_escape(str(assembly_file))}</HintPath><Private>false</Private></Reference>"
                )
            items += [f"    <Compile Include={quoteattr(msbuild_escape(path))} />" for path in additions.get(key, [])]
            items += [f"    <Compile Remove={quoteattr(msbuild_escape(item))} />" for item in removals.get(key, [])]
            condition = quoteattr(f"'$(MSBuildProjectName)' == '{project.path.stem}'")
            groups.append(f"  <ItemGroup Condition={condition}>\n" + "\n".join(items) + "\n  </ItemGroup>")
        content = "<Project>\n" + "\n".join(groups) + "\n</Project>\n"
        # MSBuild treats imported files as compile inputs: keep one path per project and rewrite it
        # only when the content changes, so unchanged assemblies stay incremental.
        project_id = hashlib.sha1(normalize(self.root).encode("utf-8")).hexdigest()[:12]
        targets_file = Path(tempfile.gettempdir()) / "unity-compile-check" / f"{project_id}.targets"
        targets_file.parent.mkdir(parents=True, exist_ok=True)
        if not targets_file.exists() or targets_file.read_text(encoding="utf-8") != content:
            targets_file.write_text(content, encoding="utf-8")
        return targets_file


def run_build(project: CsProject, targets_file: Path, root: Path):
    command = [
        "dotnet", "build", str(project.path), "--no-dependencies", "-nologo", "-v:q",
        "-clp:ErrorsOnly;NoSummary", f"-p:CustomAfterMicrosoftCommonTargets={targets_file}",
    ]
    if not project.is_sdk_style or project.restore_marker.exists():
        command.append("--no-restore")
    started = time.monotonic()
    completed = subprocess.run(
        command, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    elapsed = time.monotonic() - started
    code_errors: list[str] = []
    environment_errors: list[str] = []
    lines = (line.strip() for line in (completed.stdout + "\n" + completed.stderr).splitlines())
    for line in dict.fromkeys(lines):
        match = ERROR_PATTERN.search(line)
        if not match:
            continue
        message = PROJECT_SUFFIX.sub("", line).replace(str(root) + os.sep, "")
        code = match.group("code")
        (code_errors if code.startswith("CS") and code != "CS0006" else environment_errors).append(message)
    if completed.returncode != 0 and not code_errors and not environment_errors:
        environment_errors.append(f"dotnet build exited with {completed.returncode} and no parsable error.")
    return elapsed, code_errors, environment_errors


def check(project: UnityProject, files: list[str], dependents: bool) -> int:
    affected, additions, removals, notes = project.plan(files)
    to_build = project.with_dependents(affected) if dependents else affected
    outdated = project.stale_dependencies(to_build)
    outdated_keys = {normalize(item.path) for item in outdated}
    to_build = to_build + outdated
    csharp_count = sum(1 for file in files if file.lower().endswith(".cs"))
    print(
        f"unity-compile-check: {project.root.name}, Unity {project.version}, {csharp_count} C# file(s), "
        f"{len(to_build)} assembly(ies) to compile ({project.stale_count} stale .csproj ignored)"
    )
    for note in notes:
        print(f"  note: {note}")
    if not to_build:
        print("COMPILE_OK (no C# changes to compile)")
        return EXIT_OK
    missing = [path for item in to_build for path in item.missing_external_files()]
    if missing:
        examples = ", ".join(str(path) for path in list(dict.fromkeys(missing))[:3])
        raise UnverifiedError(
            "The generated projects reference files that do not exist, for example "
            f"{examples}. The Unity Editor they target may be missing. "
            "Regenerate project files in the installed Editor, or use Unity's own recompile."
        )
    ordered = project.build_order(to_build)
    targets_file = project.write_build_targets(ordered, additions, removals)
    code_errors: list[str] = []
    environment_errors: list[str] = []
    for item in ordered:
        elapsed, code, environment = run_build(item, targets_file, project.root)
        status = "OK" if not code and not environment else f"{len(code) + len(environment)} error(s)"
        reason = " (Unity's compiled copy is older than its sources)" if normalize(item.path) in outdated_keys else ""
        print(f"  {item.assembly}: {status} in {elapsed:.1f}s{reason}")
        code_errors += code
        environment_errors += environment
    for message in (environment_errors + code_errors)[:MAX_REPORTED_ERRORS]:
        print(f"    {message}")
    if environment_errors:
        print("COMPILE_UNVERIFIED")
        return EXIT_UNVERIFIED
    if code_errors:
        print("COMPILE_ERRORS")
        return EXIT_ERRORS
    print("COMPILE_OK")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Roslyn compile check for a Unity project's generated .csproj files.")
    parser.add_argument("--project", required=True, help="Unity project root (the folder that holds ProjectSettings/).")
    parser.add_argument(
        "--files", nargs="+", required=True, help="Changed files, relative to the project or absolute. List deleted files too."
    )
    parser.add_argument(
        "--dependents",
        action="store_true",
        help="Also compile every assembly that references a changed one. Use after public API changes.",
    )
    arguments = parser.parse_args(argv)
    try:
        if shutil.which("dotnet") is None:
            raise UnverifiedError("The dotnet SDK is not on PATH.")
        project = UnityProject(Path(arguments.project).resolve())
        return check(project, arguments.files, arguments.dependents)
    except UnverifiedError as error:
        print(f"ENVIRONMENT: {error}")
        print("COMPILE_UNVERIFIED")
        return EXIT_UNVERIFIED
    except ValueError as error:
        print(f"USAGE: {error}")
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
