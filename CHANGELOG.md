# Changelog

## [2.5.0](https://github.com/ai4os/DEEPaaS/compare/v2.4.0...v2.5.0) (2024-08-08)


### Features

* add -dev suffix to the version when installed as dev ([4d087b3](https://github.com/ai4os/DEEPaaS/commit/4d087b3e7df9f53dcfe8fb695ca23e2f55af2abf))
* add required info to help message ([d710254](https://github.com/ai4os/DEEPaaS/commit/d710254d15066643597b4cfe1c93582a711f0696))
* add types to help message ([6099f24](https://github.com/ai4os/DEEPaaS/commit/6099f24ea60bd197d6ec55f398a3b080f2c428a2))
* allow linebreaks in help messages ([2deabdb](https://github.com/ai4os/DEEPaaS/commit/2deabdbb53237373d3892bf53cb6b3f67376599f))
* allow multiple input files ([b7b1b82](https://github.com/ai4os/DEEPaaS/commit/b7b1b82c56fb9cdb6313c11fd5f4ae4352be2a33))
* properly support lists and dicts in argparse ([071b777](https://github.com/ai4os/DEEPaaS/commit/071b77784aaacbcda8a75a95adaf28c655b8846c))
* support bools ([6e1453d](https://github.com/ai4os/DEEPaaS/commit/6e1453d4d05a2e90810da9926b6207c853804643))


### Bug Fixes

* allow users to setup base_path for serving under a different prefix ([39fa910](https://github.com/ai4os/DEEPaaS/commit/39fa91035db6ec925f7f278542bbc70e534e5063)), closes [#111](https://github.com/ai4os/DEEPaaS/issues/111)
* change deprecated GH action ([71e8230](https://github.com/ai4os/DEEPaaS/commit/71e82303f91748f0e7f771aa890bb879712c800b))
* change target branch on release-please action ([32b669c](https://github.com/ai4os/DEEPaaS/commit/32b669c6e5eccac5c03cd4ce99c1b6fdd6f0ced1))
* make description optional ([7717348](https://github.com/ai4os/DEEPaaS/commit/77173480758e4c62a2c6e52009ffd82b90ee0b21))
* remove deprecated cli option ([05d7f06](https://github.com/ai4os/DEEPaaS/commit/05d7f06f07aaced23776d39641591f38472b0cd6))

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
