# eu-security-site

Static documentation site for EmpowerU LLC's open-source defensive security tooling.

It describes only the software in the three companion repositories, with links to them and short documentation pages (quick start, Wazuh pack, installer, security). It does **not** claim clients, certifications, pricing, or testimonials. Contact: bravo1alpha95@gmail.com.

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

The site is published with GitHub Pages from the `main` branch, folder `/` (root), at
<https://bravo1alpha95-dev.github.io/eu-security-site/>. `index.html` is at the root, links are
relative, and `.nojekyll` makes Pages serve the files as-is. Every merge to `main` republishes it.

A custom domain is optional. Do not commit a `CNAME` file until the domain is registered and
its DNS points at GitHub Pages.

## License

Licensed under the [Apache License 2.0](LICENSE). Copyright 2026 EmpowerU LLC.

Vulnerability reports: [SECURITY.md](SECURITY.md) and bravo1alpha95@gmail.com.
