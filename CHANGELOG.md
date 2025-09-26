# Changelog

## [3.0.0](https://github.com/ai4os/DEEPaaS/compare/v2.4.0...v3.0.0) (2025-09-26)


### ⚠ BREAKING CHANGES

* remove oslo.log and use standard python logging
* remove loading of various modules
* remove automatic loading of deprecated deepaas-test model
* remove deprecated deepaas-predict

### Features

* add -dev suffix to the version when installed as dev ([9a9602e](https://github.com/ai4os/DEEPaaS/commit/9a9602e63635bcb9dd35705a21af447cf622c114))
* add required info to help message ([77d40b4](https://github.com/ai4os/DEEPaaS/commit/77d40b437c7eae03446b1b1e952b8640a7f2e5e0))
* add types to help message ([0749057](https://github.com/ai4os/DEEPaaS/commit/0749057bc8b417a6ef4f6f79a436c97a2194699b))
* allow linebreaks in help messages ([3fd3b55](https://github.com/ai4os/DEEPaaS/commit/3fd3b552b614aedb9f84cb882d6b38e2ae5ba487))
* allow multiple input files ([ecff7f6](https://github.com/ai4os/DEEPaaS/commit/ecff7f637cd7384e5b8e167b35f78af1e01dc992))
* properly support lists and dicts in argparse ([ad1ffd7](https://github.com/ai4os/DEEPaaS/commit/ad1ffd7887fb9265267907cf27795058aad762c3))
* remove automatic loading of deprecated deepaas-test model ([376b0f9](https://github.com/ai4os/DEEPaaS/commit/376b0f905cce1c3416dbfbc61e5c91dc51db94c8)), closes [#132](https://github.com/ai4os/DEEPaaS/issues/132)
* remove deprecated deepaas-predict ([097cc83](https://github.com/ai4os/DEEPaaS/commit/097cc8303d65daf9949ab93c2e97144f172f6ce5)), closes [#154](https://github.com/ai4os/DEEPaaS/issues/154)
* remove loading of various modules ([80003c3](https://github.com/ai4os/DEEPaaS/commit/80003c328740165c735dc85d4d9d6bb0878ac41c)), closes [#128](https://github.com/ai4os/DEEPaaS/issues/128)
* remove oslo.log and use standard python logging ([033a085](https://github.com/ai4os/DEEPaaS/commit/033a085deb3605602ac6dfc9c8cb96fcd76fd6ef)), closes [#133](https://github.com/ai4os/DEEPaaS/issues/133)
* support bools ([b4f7fd3](https://github.com/ai4os/DEEPaaS/commit/b4f7fd30e0d60a7f7a6b32dfa730dbd3599dfd5c))


### Bug Fixes

* allow users to setup base_path for serving under a different prefix ([242e02e](https://github.com/ai4os/DEEPaaS/commit/242e02ee0dfb98227ff121a45636957c43e2762e)), closes [#111](https://github.com/ai4os/DEEPaaS/issues/111)
* also serve static_path from base_path ([c30db00](https://github.com/ai4os/DEEPaaS/commit/c30db00bb2798dd1f9ffb6e89bf5f2483e5d434a)), closes [#111](https://github.com/ai4os/DEEPaaS/issues/111)
* change deprecated GH action ([86886a1](https://github.com/ai4os/DEEPaaS/commit/86886a13e944f8c8ab87920e15da2abfe78dcea9))
* change target branch on release-please action ([97c8703](https://github.com/ai4os/DEEPaaS/commit/97c870393c882db5c10efe7ae2b3049029317eb1))
* do not pass basePath to aiohttp_apispec ([82a18f2](https://github.com/ai4os/DEEPaaS/commit/82a18f2465e9d0ef9e823a42dcb4772d322d039a)), closes [#111](https://github.com/ai4os/DEEPaaS/issues/111)
* make description optional ([f4e9ec4](https://github.com/ai4os/DEEPaaS/commit/f4e9ec4b1746f2a7df7e85d8304b99f05e9d61ad))
* remove deprecated cli option ([7b5896d](https://github.com/ai4os/DEEPaaS/commit/7b5896d427fcaf6ba8fb574dce4eb17f55a8b88c))


### Documentation

* fix doc build ([903e6ec](https://github.com/ai4os/DEEPaaS/commit/903e6ec9b3eb41b2149835f9a55b978477c686d9))
* update badges ([01a25db](https://github.com/ai4os/DEEPaaS/commit/01a25db8f6308dafad7a80d4bebc3f083e678aa9))
* update entry point configuration from setup.cfg to pyproject.toml ([b6afd86](https://github.com/ai4os/DEEPaaS/commit/b6afd86f6e8e3e336b03e698af86a9861b77715a))

## [2.4.0](https://github.com/ai4os/DEEPaaS/compare/v2.3.2...v2.4.0) (2024-06-07)


### Features

* deprecate deepaas-predict ([b7af423](https://github.com/ai4os/DEEPaaS/commit/b7af4231234b9b6aacb990680f00953b44385408)), closes [#154](https://github.com/ai4os/DEEPaaS/issues/154)


### Bug Fixes

* add runTest method due to pytest bug ([15fdd08](https://github.com/ai4os/DEEPaaS/commit/15fdd0815219aac3d26e7e02778194a5e69cfd1e))
* change release type version to Python ([3c801e3](https://github.com/ai4os/DEEPaaS/commit/3c801e3e483cd6336f6b70eaef219cc30d2ad3ae))
* do not use PBR to get version ([93932e5](https://github.com/ai4os/DEEPaaS/commit/93932e5ccc5373738933c5788b1265340fb2ae8f)), closes [#153](https://github.com/ai4os/DEEPaaS/issues/153)
* remove six dependency ([f0949a0](https://github.com/ai4os/DEEPaaS/commit/f0949a0a1760e462323d943e2ba9b677ef2f1df0)), closes [#164](https://github.com/ai4os/DEEPaaS/issues/164)
* update doc config and style ([81066ba](https://github.com/ai4os/DEEPaaS/commit/81066ba700fa5dd60557a37ca430dea99f5f0552))
* use a higher stacklevel on warnings ([8f3362d](https://github.com/ai4os/DEEPaaS/commit/8f3362d9f2ef94a9b22191b2aac8e13be927eb7b))


### Documentation

* add additional badges ([f89bc71](https://github.com/ai4os/DEEPaaS/commit/f89bc7192e14b88d643e8a7f1423324e80347c72))
* add additional badges ([ba9d319](https://github.com/ai4os/DEEPaaS/commit/ba9d319cac0d5bcbb24d1a5a68457604ce412640))
* create CITATION.cff ([d5a8b65](https://github.com/ai4os/DEEPaaS/commit/d5a8b65b3534a8e4d712ad6ab658c5e91aaca008)), closes [#136](https://github.com/ai4os/DEEPaaS/issues/136)
* update Jenkins badge ([#159](https://github.com/ai4os/DEEPaaS/issues/159)) ([d454121](https://github.com/ai4os/DEEPaaS/commit/d454121225ebde24cb8983a94387485fc389a1de))

## [2.3.2](https://github.com/ai4os/DEEPaaS/compare/v2.3.1...v2.3.2) (2024-04-23)


### Bug Fixes

* typo in import ([#149](https://github.com/ai4os/DEEPaaS/issues/149)) ([2c381dd](https://github.com/ai4os/DEEPaaS/commit/2c381dd1163a71e68cc5e38d4d8a98b85755813d))

## [2.3.1](https://github.com/ai4os/DEEPaaS/compare/v2.3.0...v2.3.1) (2024-03-26)


### Miscellaneous Chores

* release 2.3.1 ([#147](https://github.com/ai4os/DEEPaaS/issues/147)) ([ea9fa64](https://github.com/ai4os/DEEPaaS/commit/ea9fa64a0a7254f94ce06836163ac8664c75d38d))

## [2.3.0](https://github.com/ai4os/DEEPaaS/compare/2.2.0...v2.3.0) (2024-03-25)


### Features

* add ability to setup base path to serve the API from a custom path ([6b7874a](https://github.com/ai4os/DEEPaaS/commit/6b7874a39a25dbebcfb35f75cf7b1a782d1d37ec)), closes [#111](https://github.com/ai4os/DEEPaaS/issues/111)
* add deprecation warnings for test module ([747c7a5](https://github.com/ai4os/DEEPaaS/commit/747c7a53ccb43cd3ee63e5eddc7dd47eb50b64fb))
* add deprecation warnings when loading several models ([eee055e](https://github.com/ai4os/DEEPaaS/commit/eee055ef3ff744a1d13c4a6187ee23e698c37c15)), closes [#129](https://github.com/ai4os/DEEPaaS/issues/129)
* add option to allow to load a single module ([dce1ab5](https://github.com/ai4os/DEEPaaS/commit/dce1ab57127634333059eb81151c1e017dd2f335))
* add release-please initial configuration ([a9105fe](https://github.com/ai4os/DEEPaaS/commit/a9105fe469c742d98100a347d29bcb2d008da514)), closes [#134](https://github.com/ai4os/DEEPaaS/issues/134)
* change swagger URL from /ui to /api ([e592cae](https://github.com/ai4os/DEEPaaS/commit/e592cae10ff4b12ae1cdad139096b310bf08c584)), closes [#131](https://github.com/ai4os/DEEPaaS/issues/131)


### Bug Fixes

* [#134](https://github.com/ai4os/DEEPaaS/issues/134) ([a9105fe](https://github.com/ai4os/DEEPaaS/commit/a9105fe469c742d98100a347d29bcb2d008da514))
* [#134](https://github.com/ai4os/DEEPaaS/issues/134) ([c38f1d7](https://github.com/ai4os/DEEPaaS/commit/c38f1d776fb8a35ea4fadb28e5c6c43254d3ec17))
* remove marshmallow deprecation warnings ([b0dd6a3](https://github.com/ai4os/DEEPaaS/commit/b0dd6a3488a2701fbceb69cd98c22ac523b85534))
* remove warnings in test model ([b101b68](https://github.com/ai4os/DEEPaaS/commit/b101b6807f06ae8b16bc2794d21e6a69aa18cde1))
