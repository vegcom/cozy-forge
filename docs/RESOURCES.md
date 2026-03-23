# RESOURCES.md

References to external deps documentation

## Systemd <!-- granular per lib h2 -->

|Specifier|Expands|
|-|-|
|%n|Full unit name (`myservice@alpha.service`)|
|%p|Prefix before `@` (`myservice`)|
|%i|Instance name after `@` (`alpha`)|
|%f|Unescaped instance name|
|%u|Username for user services|
|%H|Hostname|
|%E|`$XDG_CONFIG_HOME` (user: `~/.config`)|

- <https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html>
- <https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html>

## Libraries <!-- granular per lib h2 -->

<!-- brief of includes docs and usages go here -->
