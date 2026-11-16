# Docs Pulse
Documentation-writing news reader. GitHub Actions fetches feeds into `docs/data/items.json`; a PWA in `docs/` reads it.

## Setup
1. Create a GitHub repo, push this folder.
2. Settings > Actions > General > Workflow permissions: **Read and write**.
3. Actions tab > **Update feeds** > Run workflow (first fill of data).
4. Settings > Pages > Deploy from branch `main`, folder `/docs`.
5. Open the Pages URL on Android in Chrome > menu > **Install app**.

## Add a post by hand\nAdd a line to `manual.yml` (X, LinkedIn, anything with a URL). On Android use github.com in Chrome > edit file > commit.\n\n## Change sources
Edit `feeds.yml` (in the GitHub web editor is fine). Saving it triggers a refresh. Set `enabled: false` to pause a feed.
- Substack: `https://NAME.substack.com/feed` - Medium: `https://medium.com/feed/@user` or `/feed/tag/TAG`
- YouTube: `https://www.youtube.com/feeds/videos.xml?channel_id=ID` - GitHub releases: `https://github.com/OWNER/REPO/releases.atom`
- X and LinkedIn: add under `voices:` as link cards.

Local test: `pip install feedparser pyyaml && python scripts/fetch.py && python -m http.server -d docs`
