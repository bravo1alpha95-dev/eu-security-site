# eu-security-site

Static documentation site for EmpowerU LLC's open-source defensive security tooling.

It describes only the software in the three companion repositories, with links to them, short documentation pages (quick start, Wazuh pack, installer, security), and a tutorials section under `blog/`. It does **not** claim clients, certifications, pricing, or testimonials. Contact: bravo1alpha95@gmail.com.

## Companions

- [eu-ec-detect-community](https://github.com/bravo1alpha95-dev/eu-ec-detect-community)
- [eu-wazuh-detections](https://github.com/bravo1alpha95-dev/eu-wazuh-detections)
- [eu-monitor-installer](https://github.com/bravo1alpha95-dev/eu-monitor-installer)

## Preview locally

Open `index.html` in a browser, or serve the directory with any static file server, for example:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

There are no build steps, no webfonts, and no third-party scripts.

## GitHub Pages

The site is served by GitHub Pages from the `main` branch, folder `/` (root): <https://bravo1alpha95-dev.github.io/eu-security-site/>. Links are relative and `.nojekyll` is present, so Pages serves the files as-is. Tutorials are at [`blog/`](https://bravo1alpha95-dev.github.io/eu-security-site/blog/).

Do not commit a `CNAME` file until a custom domain is intended.

## Checks

```bash
python3 tests/test_site.py
```

The check parses every page, confirms local links, fragments, and the primary navigation (including the Blog link), confirms every tutorial in `blog/` is listed on the blog index, and requests every external `https` link. GitHub Actions runs it on every push and pull request.

## License

Licensed under the [Apache License 2.0](LICENSE). Copyright 2026 EmpowerU LLC.

Vulnerability reports: [SECURITY.md](SECURITY.md) and bravo1alpha95@gmail.com.
