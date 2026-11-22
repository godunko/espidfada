
## Binding of `char*` and `const char*`

`char*` and `const char*` types are commonly used in C to transfer both string and binary data. Because C does not convey ownership transfer or memory safety rules through its type system, the following conventions are used when binding these types to Ada API:

### 1. `const char*` (Read-Only Strings)

* **String with immediate copy:** Map to `char_array_string` when the C function expects a null-terminated string and creates an internal copy of the data during the call.
* **String with persistent lifetime:** Map to `const_char_ptr` when the content is a null-terminated string, but the C API expects the application to manage and guarantee the string's lifetime for later use.

Note: this rules need to be extended for mutable/out/raw byte sequences

---

### Mapping Quick Reference

| C Parameter Type | Content Type | Ownership / Lifetime | Recommended Ada Mapping |
| :--- | :--- | :--- | :--- |
| `const char*` | Null-terminated string | Copied immediately by C | `char_array_string` |
| `const char*` | Null-terminated string | Application retains ownership | `const_char_ptr` |

## ESP-IDF Error Handling

Many ESP-IDF functions return an error code.
For each underlying C function, the Ada bindings provide _both_ of the following subprograms:

* A `function` that returns the raw ESP-IDF error code directly, allowing manual error inspection.
* A `procedure` that automatically checks the returned code via `ESPIDF.Ada_ESP_Check_Error` and raises an `ESPIDF.ESPIDF_Error` exception if an error is detected.

## Binding Incomplete C Struct Types

Incomplete C struct types are bound as `limited private` types whose full declaration is a `null record` with `Convention => C`.

Access types (pointers) for these struct types are named by appending a `_ptr` suffix to the C type name.

Example

```
   type esp_netif_t is limited private;

   type esp_netif_t_ptr is access all esp_netif_t
     with Convention => C;

private

   type esp_netif_t is limited null record
     with Convention => C;
   -- Full declaration of this type is not visible in "esp_netif.h"
```

### Binding C Types with Zero Default Initialization

When binding C struct types that require zero-initialization by default, use the Ada record template below.
This pattern ensures that any instances of the type declared in Ada are automatically initialized to zero (all bytes set to `0`) without explicit assignment, matching standard C runtime expectations for zeroed structures.

```
private with ESPIDF.Constants.Partition;

package ESPIDF.Partition is

   type esp_partition_t is limited private;

private

   type esp_partition_t is
     new C_Object_Storage
       (1 .. ESPIDF.Constants.Partition.sizeof_esp_partition_t)
   with
     Convention              => C,
     Alignment               => ESPIDF.Constants.Partition.alignof_esp_partition_t,
     Default_Component_Value => 0;

end ESPIDF.Partition;
```

```c
ESPIDFADA_SIZEOF(esp_partition_t, struct esp_partition_t);
ESPIDFADA_ALIGNOF(esp_partition_t, struct esp_partition_t);
```

## Binding Types with Non-Zero Default Initialization

For C struct types that require specific, non-zero default field values (such as configurations initialized via C macros like `HTTPD_DEFAULT_CONFIG()`), Ada bindings encapsulate the C struct as a limited, private, finalizable type.

The binding uses generated size and alignment constants and GNAT's Generalized Finalization extension via the `Finalizable` aspect. Specifying `Relaxed_Finalization => True` allows a limited record to automatically run a C-side initialization function upon object declaration.

```
private with ESPIDF.Constants.HTTP_Server;

package ESPIDF.HTTP_Server is

   type httpd_config_t is limited private;

private

   type httpd_config_t_Storage is
     new C_Object_Storage
       (1 .. ESPIDF.Constants.HTTP_Server.sizeof_httpd_config_t)
   with
     Convention => C,
     Alignment  => ESPIDF.Constants.HTTP_Server.alignof_httpd_config_t;

   procedure Initialize (Self : in out httpd_config_t);

   type httpd_config_t is limited record
      Storage : httpd_config_t_Storage;
   end record
   with
     Convention  => C,
     Alignment   => ESPIDF.Constants.HTTP_Server.alignof_httpd_config_t,
     Finalizable =>
       (Initialize           => Initialize,
        Relaxed_Finalization => True);

   pragma Compile_Time_Error
     (httpd_config_t'Size /= ESPIDF.Constants.HTTP_Server.sizeof_httpd_config_t
        * C_Storage_Element'Size,
      "httpd_config_t size does not match C");

end ESPIDF.HTTP_Server;
```

```
   ----------------
   -- Initialize --
   ----------------

   procedure Initialize (Self : in out httpd_config_t) is

      procedure Imported (config : out httpd_config_t)
        with Import, Convention => C,
             External_Name => "__ada_HTTPD_DEFAULT_CONFIG";

   begin
      Imported (Self);
   end Initialize;
```

```
ESPIDFADA_SIZEOF(httpd_config_t, httpd_config_t);
ESPIDFADA_ALIGNOF(httpd_config_t, httpd_config_t);

void __ada_HTTPD_DEFAULT_CONFIG(httpd_config_t *cfg)
{
    *cfg = (httpd_config_t)HTTPD_DEFAULT_CONFIG();
}
```

## Generating C Type Metadata

Each component owns its probe and generated Ada package. Put the probe macros
in a dedicated `tools/<component>_constants.c`, separate from C accessor and
initializer functions. Only the latter belong in the linked C bridge.

For example, `tools/gpio_constants.c` contains:

```c
#include "driver/gpio.h"
#include "private/espidfada_constants.h"

ESPIDFADA_SIZEOF(gpio_config_t, gpio_config_t);
ESPIDFADA_ALIGNOF(gpio_config_t, gpio_config_t);
```

The first argument is a stable Ada identifier; the second is the exact C type,
including a `struct` tag when required. Only type sizes and alignments are
supported. Enum values, field offsets and arbitrary expressions are outside
this interface.

Declare the Alire dependency on `espidfada`, and the CMake dependency on
`espidfada` and the relevant SDK drivers. Register the probe after
`idf_component_register`:

```cmake
idf_component_register(SRCS source/espidfada_driver_gpio.c
    PRIV_REQUIRES espidfada esp_driver_gpio)
idf_component_get_property(espidfada_dir espidfada COMPONENT_DIR)
include("${espidfada_dir}/cmake/constants.cmake")
espidfada_generate_constants(NAME GPIO SOURCE tools/gpio_constants.c)
```

The helper inherits the requesting component's compile environment and keeps
the probe header private to the probe target. It compiles an unlinked object,
then uses target `nm` to emit `ESPIDF.Constants.GPIO` as
`.gens/espidf-constants-gpio.ads`. It rejects invalid names, duplicate constants
and empty or malformed metadata. Writes are atomic; unchanged contents retain
their timestamp. `PACKAGE` overrides the package name and its GNAT filename;
the caller must provide any additional parent packages. `OUT_TARGET <variable>`
returns the per-registration generation target. Duplicate output registrations
are configuration errors.

Add `.gens` to GPR `Source_Dirs` and `/.gens/` to `.gitignore`; do not commit
generated Ada sources. Use generated named numbers for storage bounds and
`Alignment`. For record wrappers, check the outer record's size and alignment
as well as its storage type. Preserve C conventions and initialization.

The application's `espidf_add_ada_application` call must specify
`DEPENDS espidfada_constants` so probe compilation and Ada generation finish
before Alire/GPR starts. Depending only on the final component library does
not establish that order. The runtime's existing constants target remains
separate; `espidfada` has no dependency on the runtime.

Use `idf.py espidfada_constants` for generation without a firmware build.
A clean checkout must generate constants before a direct `alr build`.
Direct Alire builds reuse existing files without freshness checks; regenerate
through IDF after target, SDK, or configuration changes. One component source
tree holds one generated configuration at a time. Simultaneous configurations
require separate checkouts; unchanged-content writes do not make shared
checkouts safe.

## C Glue Code

C glue code of the binding crate can be compiled only inside the ESP-IDF build environment, while Alire builds the crate standalone (e.g. when publishing).
To support both cases, project file of the crate that contains C sources should use the list of languages provided by the `espidf` crate:

```
   for Languages use ESPIDF.Crate_Languages_Ada_C;
```

It contains only `"Ada"` by default, and both `"Ada"` and `"C"` when the application sets the `espidf.Build_Environment` configuration variable to `"espidf"`.

Project files of crates without C sources don't need to specify languages.

## Documentation

Conventions for documenting bindings in GNATdoc format are described in [DOCUMENTATION.md](DOCUMENTATION.md).
