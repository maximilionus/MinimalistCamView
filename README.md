![](./MinimalistCamView/data/icons/mcv_icon.png)
# Minimalist Cam View
- [Minimalist Cam View](#minimalist-cam-view)
  - [Main Information](#main-information)
  - [How to run](#how-to-run)
  - [Arguments](#arguments)

## Main Information
**Minimalist Cam View** is a python application with gui support for viewing and recording any camera stream. Application is currently under development, so some features may not work as expected.

## How to run
1. Install [`poetry`](https://github.com/python-poetry/poetry) dependency manager with `pip` or [from source](https://github.com/python-poetry/poetry#installation).
2. Go to cloned `MinimalistCamView` repository folder and run:
   ```bash
   poetry install --no-dev
   ```
3. After all packages successfully installed, run:
   ```bash
   poetry run mcv
   ```

## Arguments
| Arg             | Description                                              |
| :-------------- | :------------------------------------------------------- |
| `--only-record` | Run MCV in non-gui mode and start the recording from cam |
| `--quiet`       | Disable logging to file                                  |
| `-v`            | Log everything with level of logging set to `NOTSET`     |