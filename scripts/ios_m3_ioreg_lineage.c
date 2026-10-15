/*
 * Read-only IOService-plane lineage snapshot for IOS-M3 diagnostics.
 * Source-only candidate: NOT installed, NOT a boot proof, NOT an iOS build.
 * Actual iOS target compilation and runtime verification remain outstanding.
 */
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#ifdef IOS_M3_HOST_TEST
#include "ios_m3_ioreg_test_shim.h"
#else
#include <IOKit/IOKitLib.h>
#endif

#define IOS_M3_MAX_ENTRIES 4096U

static void json_string(const char *s)
{
    const unsigned char *p = (const unsigned char *)s;
    putchar('"');
    while (*p != 0) {
        unsigned char c = *p++;
        if (c == '"' || c == '\\') {
            putchar('\\');
            putchar((int)c);
        } else if (c < 0x20) {
            printf("\\u%04x", (unsigned)c);
        } else {
            putchar((int)c);
        }
    }
    putchar('"');
}

static bool emit_entry(io_registry_entry_t entry)
{
    uint64_t entry_id = 0;
    kern_return_t kr = IORegistryEntryGetRegistryEntryID(entry, &entry_id);
    if (kr != KERN_SUCCESS) {
        printf("{\"kind\":\"entry_error\",\"step\":\"entry_id\",\"status\":%d}\n", (int)kr);
        return false;
    }

    io_name_t name;
    io_name_t class_name;
    kr = IORegistryEntryGetName(entry, name);
    if (kr != KERN_SUCCESS) {
        printf("{\"kind\":\"entry_error\",\"step\":\"name\",\"id\":\"0x%016" PRIx64 "\",\"status\":%d}\n", entry_id, (int)kr);
        return false;
    }
    kr = IOObjectGetClass(entry, class_name);
    if (kr != KERN_SUCCESS) {
        printf("{\"kind\":\"entry_error\",\"step\":\"class\",\"id\":\"0x%016" PRIx64 "\",\"status\":%d}\n", entry_id, (int)kr);
        return false;
    }

    io_registry_entry_t parent = 0;
    uint64_t parent_id = 0;
    kern_return_t parent_status = IORegistryEntryGetParentEntry(entry, kIOServicePlane, &parent);
    if (parent_status == KERN_SUCCESS) {
        kern_return_t id_status = IORegistryEntryGetRegistryEntryID(parent, &parent_id);
        IOObjectRelease(parent);
        if (id_status != KERN_SUCCESS) {
            parent_status = id_status;
        }
    }

    printf("{\"kind\":\"entry\",\"plane\":\"IOService\",\"id\":\"0x%016" PRIx64 "\",\"parent_id\":", entry_id);
    if (parent_status == KERN_SUCCESS) {
        printf("\"0x%016" PRIx64 "\"", parent_id);
    } else {
        fputs("null", stdout);
    }
    printf(",\"parent_status\":%d,\"class\":", (int)parent_status);
    json_string(class_name);
    fputs(",\"name\":", stdout);
    json_string(name);
    fputs("}\n", stdout);
    return true;
}

int main(void)
{
    io_iterator_t iterator = 0;
    kern_return_t status = IORegistryCreateIterator(
        kIOMasterPortDefault, kIOServicePlane, kIORegistryIterateRecursively, &iterator);
    if (status != KERN_SUCCESS) {
        printf("{\"kind\":\"error\",\"step\":\"iterator\",\"status\":%d}\n", (int)status);
        return 2;
    }

    unsigned count = 0;
    unsigned errors = 0;
    io_registry_entry_t entry;
    while (count < IOS_M3_MAX_ENTRIES && (entry = IOIteratorNext(iterator)) != 0) {
        if (!emit_entry(entry)) {
            ++errors;
        }
        IOObjectRelease(entry);
        ++count;
    }
    /* Conservative: reaching the cap is treated as truncation, even at exact size. */
    bool truncated = count == IOS_M3_MAX_ENTRIES;
    IOObjectRelease(iterator);
    printf("{\"kind\":\"summary\",\"plane\":\"IOService\",\"entries\":%u,\"errors\":%u,\"truncated\":%s,\"full_system_boot_accepted\":false}\n",
           count, errors, truncated ? "true" : "false");
    return errors == 0 && !truncated ? 0 : 3;
}
