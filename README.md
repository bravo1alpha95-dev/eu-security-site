# eu-security-site

Static documentation site for EmpowerU LLC's open-source defensive security tooling.

It describes only the software in the three companion repositories, with links to them and short documentation pages (quick start, Wazuh pack, installer, security). It does **not** claim clients, certifications, pricing, or testimonials. Contact is shown as `[CONTACT EMAIL]` until a real address is published.

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

## GitHub Pages (not enabled)

This repository is ready to be served by GitHub Pages: `index.html` is at the root, links are relative, and `.nojekyll` is present so Pages would serve the files as-is.

**GitHub Pages is not enabled.** Enabling it would make the site public. To enable it later, after you have reviewed this repository and decided to publish:

1. Make the repository public, or keep it private and use GitHub Pages under a plan that allows private Pages, as you prefer.
2. In the repository **Settings → Pages**, set the source to the `main` branch, folder `/` (root), and save.
3. Optionally add a custom domain. Do not commit a `CNAME` file until that domain is intended.

Do not run those steps until you are ready for the site to be reachable.

## License

Licensed under the [Apache License 2.0](LICENSE). Copyright 2026 EmpowerU LLC.

Vulnerability reports: [SECURITY.md](SECURITY.md) and `[CONTACT EMAIL]`.
