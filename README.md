k8sdoc-epub
===

Generate Kubernetes documentation in EPUB format.

[Download EPUB from releases](https://github.com/unknown321/k8sdoc-epub/releases/latest)

KOBO users should use `kepub.epub` version.

### Known issues

  - links to other documentation pages are broken
  - rendering might be broken on e-readers (tested on KOBO only)
  - TOC is flattened
  - missing EPUB cover

### Build

Install pip dependencies:

```shell
make prepare
```

### Run

```shell
make run
```