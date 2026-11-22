# ESP-IDF/Ada

Base types and shared utilities for Ada bindings to the Espressif IoT Development Framework (ESP-IDF). Peripheral and service bindings are provided by separate crates.

## Ecosystem

The following crates build upon this base layer:

 * [espidf_console](https://github.com/godunko/espidf_console): binding of ESP-IDF Console
 * [espidf_driver_gpio](https://github.com/RREE/espidf_driver_gpio): bindings for setting and reading GPIOs
 * [espidf_driver_i2c](https://github.com/godunko/espidf_driver_i2c): bindings of the I2C peripheral driver
 * Event Loop Library ([espidf_event](https://github.com/godunko/espidf_event))
 * FAT Filesystem Support ([espidf_fatfs](https://github.com/godunko/espidf_fatfs))
 * HTTP Server ([espidf_http_server](https://github.com/godunko/espidf_http_server))
 * mDNS Service ([espidf_mdns](https://github.com/godunko/espidf_mdns))
 * ESP-NETIF ([espidf_netif](https://github.com/godunko/espidf_netif))
 * Non-Volatile Storage Library ([espidf_nvs_flash](https://github.com/godunko/espidf_nvs_flash))
 * Partitions API ([espidf_partition](https://github.com/godunko/espidf_partition))
 * SPIFFS Filesystem ([espidf_spiffs](https://github.com/godunko/espidf_spiffs))
 * Wear Levelling API ([espidf_wear_levelling](https://github.com/godunko/espidf_wear_levelling))
 * USB Device Stack ([espidf_tinyusb](https://github.com/godunko/espidf_tinyusb))
   * Mass Storage Class ([espidf_tinyusb_msc](https://github.com/godunko/espidf_tinyusb_msc))
 * Wi-Fi ([espidf_wifi](https://github.com/godunko/espidf_wifi))

## Getting Started: Project Template

Start with a project template for your MCU:

 * For ESP32-C3 (RISC-V): [ESP32C3 Project Template](https://github.com/godunko/esp32c3_template)
 * For ESP32 (Xtensa, LX6): [ESP32 Project Template](https://github.com/RREE/esp32_template)
 * For ESP32-S3 (Xtensa, LX7): [ESP32S3 Project Template](https://github.com/godunko/esp32s3_template)

## Usage

After setting up the project template:

1. Ada Dependencies: Use Alire to include the binding's crates into your Ada application.

```
alr with espidf_console
alr with espidf_driver_i2c
```

2. ESP-IDF Components: Make the binding's ESP-IDF/Ada component available to
ESP-IDF (for example, under `components/` or through `EXTRA_COMPONENT_DIRS`)
and list it in your application's `main/CMakeLists.txt`. For example, an
application using the GPIO binding declares:

```cmake
idf_component_register(
    REQUIRES espidfada_driver_gpio)
```

The binding component declares its native ESP-IDF dependencies through
`REQUIRES` or `PRIV_REQUIRES`. For example, `espidfada_driver_gpio` declares
`PRIV_REQUIRES esp_driver_gpio espidfada`. ESP-IDF resolves these dependencies
and links the required libraries transitively; the application does not need to
repeat `esp_driver_gpio` in its requirements or in an `add_prebuilt_library`
call. See [ESP-IDF component requirements](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/build-system.html#component-requirements).

Adding an Alire dependency alone does not register an ESP-IDF component.
For a binding without ESP-IDF component integration, the application still
needs to declare the native ESP-IDF dependencies explicitly. Also declare any
native ESP-IDF components used directly by the application's C sources.

3. Build

Run `idf.py build` to compile and link the application.

## Generated binding constants

For bindings that use generated constants, add `DEPENDS espidfada_constants`
to the application's `espidf_add_ada_application` call:

```cmake
espidf_add_ada_application(
    TARGET "${COMPONENT_LIB}"
    PROJECT_DIR "${PROJECT_DIR}"
    OBJECT ".objs/app_main.o"
    DEPENDS espidfada_constants)
```

Build through `idf.py build` to generate constants for the current target and
configuration. Before using `alr build` directly, run
`idf.py espidfada_constants`; regenerate after changing the target, SDK, or
`sdkconfig`. Direct Alire builds do not check whether generated files are current.

Use separate component/crate checkouts for simultaneous builds with different
configurations.

For binding authoring instructions, see
[CONTRIBUTING.md](CONTRIBUTING.md#generating-c-type-metadata).
