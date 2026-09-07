---
name: steam-store-launch
description: Use when planning, drafting, auditing, or launching a Steam Coming Soon or store page for an indie game, including Steamworks requirements, capsules, screenshots, trailer, copy, tags, wishlist strategy, competitor research, press and creator CRM, festivals, Steam Next Fest, Reddit/social announce posts, UTM tracking, and launch readiness.
---

# Steam Store Launch

Use this skill to help a game get from "we need a Steam page" to a public,
wishlist-ready Coming Soon page with a supporting marketing plan.

## First Steps

1. Identify the game's genre, player fantasy, hook, platform targets, release
   window, demo status, competitors, and current visual assets.
2. Check the current official Steamworks docs before giving date-sensitive or
   asset-sensitive advice. Steam requirements, capsule templates, festival
   dates, and review timing can change.
3. Decide the work mode:
   - **Page setup**: Steamworks checklist, assets, trailer, copy, tags.
   - **Page audit**: find missing/weak items before Valve review.
   - **Marketing prep**: competitor research, CRM, wishlist beats, festivals.
   - **Launch campaign**: announcement posts, outreach, UTM tracking, follow-up.

## Core Workflow

1. **Readiness gate**
   - Do not recommend opening the page publicly if the art direction, core
     feature set, screenshots, and short hook are still unstable.
   - Flag any feature shown in screenshots/trailers/copy that will not be in the
     release or demo build.

2. **Steamworks checklist**
   - Use `references/steamworks-store-page.md` for current Steam page, review,
     assets, tags, UTM, wishlist, and Next Fest guidance.
   - Produce a gap list with owner, priority, blocker status, and next action.

3. **Positioning and copy**
   - Start from the game's strongest visible gameplay promise, not lore.
   - Draft short description, long description sections, feature bullets,
     capsule text constraints, tags, and localization notes.
   - Keep copy specific, honest, and player-facing.

4. **Asset and trailer plan**
   - List required capsule/library assets, screenshot needs, trailer beats, and
     store-page extra assets.
   - Prefer actual gameplay screenshots and clips. Avoid concept-only,
     cinematic-only, fake UI, awards, external links, and unsupported claims.

5. **Competitor and CRM research**
   - Use `references/marketing-crm-playbook.md` when the task involves press,
     creators, X/Twitter, journalists, streamers, platform accounts, hashtags,
     or competitor discovery.
   - Use `references/how-to-market-a-game-index.md` when the task needs indie
     Steam marketing research patterns, wishlist benchmarks, Steam Next Fest
     context, social post examples, genre/market analysis, or article sources
     from HowToMarketAGame.
   - Build a CRM table with source URL, relevance reason, contact channel,
     audience fit, priority, last touch, and next action.

6. **Wishlist and announcement campaign**
   - Use `references/wishlist-campaign.md` for announce beats, Reddit/social
     patterns, Steam events, cross-promotion, creator outreach, and UTM naming.
   - Separate channels by goal: wishlist conversion, awareness, creator
     coverage, festival fit, demo feedback, and community validation.

7. **Review output**
   - End with clear deliverables: missing assets, Steamworks blockers, copy
     drafts, CRM targets, outreach calendar, post ideas, and validation steps.
   - Include sources and dates for any researched festival, journalist, creator,
     or Steamworks rule.

## Output Templates

For a page setup or audit, return:

```text
Steam Page Readiness
- Verdict: Ready / Needs Work / Blocked
- Blockers:
- High-impact improvements:
- Required Steamworks actions:
- Assets needed:
- Copy/tags needed:
- Review timing:
- Next 5 actions:
```

For CRM work, return:

```text
CRM Columns
- Name
- Type: journalist / creator / platform / studio / festival / community
- Outlet/channel
- Why they fit
- Competitor/source link
- Contact link
- Priority
- Suggested angle
- Last touch
- Next action
```

## Coordination

- Use `game-design-studio` when the Steam hook, audience, core loop, or genre
  positioning is unclear.
- Use `game-code-review` or `unity-game-dev` only if the Steam page claims need
  verification against the actual build.
- Use `game-studio-orchestration` for full pre-release, Next Fest, or launch
  campaigns that involve design, production, QA, community, and release work.
