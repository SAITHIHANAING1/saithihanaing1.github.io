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

## Publish on GitHub Pages
The local history contains an old version of the site with a phone number, so publish a fresh
history with one commit instead of pushing this branch.

1. Run `python tests/check_site.py` and make sure it prints `OK`.
2. Create an empty public repo on GitHub, for example `SAITHIHANAING1/portfolio`.
3. Publish a clean copy with no history:
   ```
   git checkout --orphan publish
   git add -A
   git commit -m "Portfolio site"
   git remote add origin https://github.com/SAITHIHANAING1/portfolio.git
   git push -u origin publish:main
   ```
4. In the repo: **Settings → Pages → Build and deployment**, source **Deploy from a branch**,
   branch `main`, folder `/ (root)`. The site appears at
   `https://saithihanaing1.github.io/portfolio/` after a minute.
5. If you named the repo something other than `portfolio`, update `og:image` and `og:url` in
   `index.html` so LinkedIn shows your photo in the link preview.

## Add the student domain
1. Claim the free domain from the GitHub Student Developer Pack
   (https://education.github.com/pack), for example on Name.com or Namecheap.
2. In the repo: **Settings → Pages → Custom domain**, enter the domain (e.g. `saithihanaing.dev`)
   and save. GitHub commits a `CNAME` file for you.
3. At the registrar, add the DNS records:
   - Four `A` records for the bare domain (`@`):
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - A `CNAME` record for `www` pointing to `saithihanaing1.github.io`
4. When the DNS check turns green (can take up to a day), tick **Enforce HTTPS**.
5. Change `og:image` and `og:url` in `index.html` to the new domain.

Check the current IPs in GitHub's docs ("Managing a custom domain for your GitHub Pages site")
before adding them.
