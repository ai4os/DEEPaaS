# Changelog

## [2.6.0](https://github.com/ai4os/DEEPaaS/compare/v2.5.2...v2.6.0) (2024-11-11)


### Features

* disable poetry groups (not compatible with Python 3.6) ([a492900](https://github.com/ai4os/DEEPaaS/commit/a492900d2350023de445c362cfa02b46e3639590))
* make requirements compatible with Python 3.6 ([c9ca14d](https://github.com/ai4os/DEEPaaS/commit/c9ca14d84e560e0c6ff14e083426e07f260bcd70))
* stop using `importlib.metadata` incompatible with 3.6 ([c0178b7](https://github.com/ai4os/DEEPaaS/commit/c0178b7016dbaccedb88421b1f541db4c1d18127))

## [2.5.2](https://github.com/ai4os/DEEPaaS/compare/v2.5.1...v2.5.2) (2024-08-27)


### Bug Fixes

* merge from releases/2.x, replace return with log.info() ([ce1a46a](https://github.com/ai4os/DEEPaaS/commit/ce1a46ae6a67cfeafe3fa9bbd18feb112115b477))
* merge from releases/2.x, replace return with log.info() ([8b71eaf](https://github.com/ai4os/DEEPaaS/commit/8b71eafe6d8e8d55394a7d5bd4ca3c38e3fc15c1))
* merge from releases/2.x, replace return with log.info() ([35033e4](https://github.com/ai4os/DEEPaaS/commit/35033e4ee0443c4ed6b7517aecb9e69178264f10))
* merge ifs statements ([32a3f52](https://github.com/ai4os/DEEPaaS/commit/32a3f52934ba083f9beafe80f82fb057035206f5))
* merge pull request [#187](https://github.com/ai4os/DEEPaaS/issues/187) from ai4os/fix/cli-upd ([93583ee](https://github.com/ai4os/DEEPaaS/commit/93583eea700cc47e6220a0f68a0fbc2302db73ab))
* prepare deepaas-cli for the release 2.x ([1d9facd](https://github.com/ai4os/DEEPaaS/commit/1d9facda7229ff1df1830a08b8e03be3e9269d9f))
* remove unused imports ([4c9c5de](https://github.com/ai4os/DEEPaaS/commit/4c9c5ded42b2b679c354b2a1d0c2f4e83c7cbb55))
* remove unused parameter in function ([6d870d9](https://github.com/ai4os/DEEPaaS/commit/6d870d9670ccc5e9802d29c4289c06ccc2c5fc09))
* remove W-I-P test for cli ([a0a1780](https://github.com/ai4os/DEEPaaS/commit/a0a178010d37a1df3b3d5976d7646764cf49d20f))

## [2.5.1](https://github.com/ai4os/DEEPaaS/compare/v2.5.0...v2.5.1) (2024-08-09)


### Bug Fixes

* also serve static_path from base_path ([267ab6a](https://github.com/ai4os/DEEPaaS/commit/267ab6ad6848757b8cc0a2dfb58e15c80ec0de28)), closes [#111](https://github.com/ai4os/DEEPaaS/issues/111)
* do not pass basePath to aiohttp_apispec ([45c8452](https://github.com/ai4os/DEEPaaS/commit/45c84525566285f089bf82415e337a9adca14fe7)), closes [#111](https://github.com/ai4os/DEEPaaS/issues/111)

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
