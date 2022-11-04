## Braket Build Tools

## Installing the Amazon Braket Build Tools

The Amazon Braket Build Tools can be installed with pip as follows:

```bash
pip install amazon-braket-build-tools
```

You can also install from source by cloning this repository and running a pip install command in the root directory of the repository:

```bash
git clone https://github.com/aws/amazon-braket-build-tools.git
cd amazon-braket-build-tools
pip install .
```

### Flake8 Checkstyle Plugin

This tool checks python source code for Braket checkstyle standards as a Flake8 plugin.
Installing amazon-braket-build-tools automatically registers this plugin with flake8 and
will be run by default whenever flake8 is used.

#### Testing The Installation
To test if the extension has been installed run:
```bash
flake8 --enable-extensions=BCS --help
```
At the bottom of the output you should see braket checkstyle among your installed plugins:
```
Installed plugins: braket.flake8_plugins.braket_checkstyle_plugin: 0.1.0
```

#### Running
To run with the extension enabled, just run flake8 on the module of your choice.
For example:
```bash
flake8 --enable-extensions=BCS src
```


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

