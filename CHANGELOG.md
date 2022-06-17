# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [2.1.0]
### Added
### Changed
- DEEPaaS dependency on Python is relaxed, again, to >= 3.6

### Deprecated
### Removed
### Fixed
### Security

## [2.0.0]
### Added
### Changed
- DEEPaaS now requires Python >= 3.7
- Start using a changelog.

### Deprecated
### Removed
- Drop support for V1 API.

### Fixed
- Fix broken multiprocessing API in some Python versions (#95)
- Updated documentation.

### Security

## [1.3.0] - 2020-04-22
### Added
- New `deepaas-cli` command line tool.

### Changed
- Decoupled API from ModelWrapper class.

## [1.2.1] - 2020-03-06
### Changed
- Include original filename in UploadedFile objects.

### Fixed
- Fix GPU OOM, not using anymore separated train and predict pools (#87).

## [1.2.0] - 2020-03-02
### Added
- Add deepaas-execute command.

### Changed
- Pin webargs version <6.0.0 (#82).
- OpenWhisk: set debug as specified by user.
- OpenWhisk: set client_max_size also on OpenWhisk proxy.
- Improved documentation.

### Fixed
- Fixed unit tests.

## [1.1.1] - 2020-02-19
### Fixed
- Use `spawn` method rather than `fork` for the training process pool.

## [1.1.0] - 2020-02-18
### Changed
- Remove vendorized aiohttp-apispec.
- Include `training_args`, `training_output` and `training_duration` to the `train_response`.

### Fixed
- Fixed unit tests.

## [1.0.1] - 2020-02-10
### Changed
- Vendorize aiohttp-apispec.

### Fixed
- Correctly handle swagger links (UI and spec file).
- Fixed unit tests.
- Fix cancellation of trainings.
- Update documentation.

## [1.0.0] - 2020-01-21
### Changed
- Drop Flask in favour of aiohttp. This large patchet drops Flask and
  Flask-RESTPlus in favour of aiohttp, aiohttp-apispec, marshmallow and webargs
  in order to implement asyncrhonous requests. We still maintain v1, alhtough
  marked as depreated.

### Added
- New API (V2) and new model wrappers (v2) are introduced.

### Deprecated
- API V1 is marked as deprecated and staged for removel in the next release.

## [0.5.2] - 2020-09-05
### Fixed
- Fix documentation build error.

## [0.5.1] - 2019-08-23
### Fixed
- Fix test arguments and parser, in order to be consistent with the previous
  version of DEEPaaS, in which we returned a list of len 1 (because of the
  Swagger bug) for the args['files'] parameter in the predict_data method.


## [0.5.0] - 2019-07-23
### Changed
Improve unit testing.
Improve documentation.

### Fixed
Fix dependency on gevent.

## [0.4.1] - 2019-07-17
### Changed
Updated Dockerfile.

## [0.4.0] - 2019-06-06
### Added
Add initial version of paper for Journal of Open Source Software.

### Fixed
Handle SIGTERM signal explicitly for better Docker execution.
Improve CI/CD integration

## [0.3.0] - 2019-02-20
### Added
Add support to run DEEPaaS as an OpenWhisk Docker action.

### Changed
Update documentation.

## [0.2.0] - 2019-01-14
### Added
- Initial support for passing down training arguments to underlying models.
  This version implements the loading of arguments for each model. Since
  different models would have different arguments, we need to pre-populate the
  API with those routes.

## [0.1.2] - 2018-12-04
### Fixed
- Fix PyPi classifiers.
- Fix documentation automated generation.

## [0.1.1] - 2018-12-04
### Added
- Initial documentation.

### Fixed
- Testing and CI/CD improvements.

## [0.1.0] - 2018-10-26
### Changed
- Initial release.
