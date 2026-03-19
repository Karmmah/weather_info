# EXW

**TODO: Add description**

## Installation

If [available in Hex](https://hex.pm/docs/publish), the package can be installed
by adding `weather_info` to your list of dependencies in `mix.exs`:

```elixir
def deps do
  [
    {:weather_info, "~> 0.1.0"}
  ]
end
```

Documentation can be generated with [ExDoc](https://github.com/elixir-lang/ex_doc)
and published on [HexDocs](https://hexdocs.pm). Once published, the docs can
be found at <https://hexdocs.pm/weather_info>.

## Settings

- add Town that you want to display weather to at the top of the locations in the config

## Custom setup steps

- create bootable alpine sd card
- add headless file from alpine wiki in root of sd card
- add wpa_supplicant.conf in root of sd card
- boot pi and log into root (has no password)
- run setup-alpine (also set up the wifi connection again even though already connected)
- log into pi as the user (login as root does not work anymore)
- enable community repos in /etc/apk/repositories
- move owm_token.txt into project directory
- install elixir and dependencies with "mix deps.get"

- 
- set up venv (python3 -m venv venv; . venv/bin/activate)
- install python modules (pip install: spidev, pillow, gpiod, RPi.GPIO, numpy)
- run iex -S mix as root (enter su, needed to be able to acces gpio pins; apparently not needed only on raspberry os)
