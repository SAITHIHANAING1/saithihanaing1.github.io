# Sai Thiha Naing: portfolio

Personal portfolio site: AI & data engineer, computer vision on edge hardware.
Plain HTML, CSS and a few lines of JavaScript. No build step.

## Pages
- `index.html`: home (hero, experience, featured projects, skills, education, contact)
- `academic_projects.html`: school projects
- `personal_projects.html`: personal projects
- `styles.css`: the whole design ("Annotated" look, light and dark)
- `script.js`: optional draw-in of the detection boxes on the photo
- `images/headshot.jpg`: keep it under 300 KB

## Preview locally
```
python -m http.server 8000
```
Then open http://localhost:8000.

## Check before publishing
```
python tests/check_site.py
```
Prints `OK` when there are no placeholders, dead links, broken local links, phone number,
oversized images or leftover old styles.

Rules for content: no private project names (listed in the untracked `tests/banned_local.txt`),
and nothing about the Japfa computer vision project beyond the tool stack until Japfa says it can
be shared. The checker also scans every file that would be pushed, not just the pages.

## Live site
https://saithihanaing1.github.io/ (repo `SAITHIHANAING1/saithihanaing1.github.io`,
GitHub Pages from `main`, root folder).

## Updating the site
Work on the local branch `publish`, which tracks `origin/main`. The other local branches
contain an old version of the site with a phone number in their history, so never push them.

```
python tests/check_site.py   # must print OK
git add -A
git commit -m "Describe the change"
git push
```
The live site updates about a minute after the push.

## Add a custom domain later
1. Buy the domain (Cloudflare Registrar sells `.com` at cost, about US$10–11 a year).
2. In the repo: **Settings → Pages → Custom domain**, enter the domain (e.g. `saithihanaing.com`)
   and save. GitHub commits a `CNAME` file for you.
3. At the registrar, add the DNS records:
   - Four `A` records for the bare domain (`@`):
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - A `CNAME` record for `www` pointing to `saithihanaing1.github.io`
4. When the DNS check turns green (can take up to a day), tick **Enforce HTTPS**.
5. Change `og:image` and `og:url` in `index.html` to the new domain.

Check the current IPs in GitHub's docs ("Managing a custom domain for your GitHub Pages site")
before adding them.
