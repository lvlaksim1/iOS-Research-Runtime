#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def replace_exact(relative_path: str, old: str, new: str) -> None:
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"expected source block not found in {relative_path}")
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8", newline="\n")

replace_exact(
    "hw/arm/darwin.c",
    """static mmap_file_t check_and_open(const char *path, const char *errmsg) {
    int fd;
    struct stat stats;
    void *mapping;

    if (!path) goto fail;

    fd = open(path, O_RDONLY | O_BINARY);
    if (fd < 0) goto fail;

    fstat(fd, &stats);
    mapping = mmap(NULL, stats.st_size, PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0);
    if (MAP_FAILED == mapping) goto fail;

    if (is_im4p(mapping)) {
        fprintf(stderr, "error: %s is an im4p, you need to unwrap it (eg. ipsw img4 im4p extract)\\n", path);
        goto fail;
    }

    return (mmap_file_t){
        .buf = mapping,
        .len = stats.st_size,
    };

fail:
    fprintf(stderr, "%s\\n", errmsg);
    exit(1);
}
""",
    """static mmap_file_t check_and_open(const char *path, const char *errmsg) {
    gchar *contents = NULL;
    gsize length = 0;

    if (!path) goto fail;

    /*
     * The original Darwin machine used POSIX mmap(MAP_PRIVATE) to obtain a
     * writable private copy of each firmware blob. GLib gives the same
     * semantics on Windows: a writable heap buffer owned by the caller.
     */
    if (!g_file_get_contents(path, &contents, &length, NULL)) goto fail;

    if (is_im4p(contents)) {
        fprintf(stderr, "error: %s is an im4p, you need to unwrap it (eg. ipsw img4 im4p extract)\\n", path);
        g_free(contents);
        exit(1);
    }

    return (mmap_file_t){
        .buf = contents,
        .len = length,
    };

fail:
    fprintf(stderr, "%s\\n", errmsg);
    exit(1);
}
""",
)

replace_exact(
    "hw/arm/darwin.c",
    """    munmap(info->bootkc_f.buf, info->bootkc_f.len);
    munmap(info->dtree_f.buf, info->dtree_f.len);
    munmap(info->tc_f.buf, info->tc_f.len);
    munmap(info->ramdisk_f.buf, info->ramdisk_f.len);
    if (info->sptm) {
        munmap(info->sptm_f.buf, info->sptm_f.len);
        munmap(info->txm_f.buf, info->txm_f.len);
    }
""",
    """    g_free(info->bootkc_f.buf);
    g_free(info->dtree_f.buf);
    g_free(info->tc_f.buf);
    g_free(info->ramdisk_f.buf);
    if (info->sptm) {
        g_free(info->sptm_f.buf);
        g_free(info->txm_f.buf);
    }
""",
)

replace_exact(
    "hw/arm/xnuboot_sptm.c",
    '#include <sys/mman.h>\n',
    '',
)

replace_exact(
    "hw/arm/apple_dtree.c",
    """struct dtree_node *adt_find_node(struct dtree_node *root, const char *path) {
    char *token, *string, *tofree;
    struct dtree_node *cur_node, *cur_child;

    tofree = string = strdup(path);
    cur_node = root;

    while (NULL != (token = strsep(&string, kDTPathNameSeparator))) {
        bool found_it = false;

        cur_child = first_child(cur_node);
        for (size_t i = 0; i < cur_node->nChildren; i++) {
            if (0 == strcmp(adt_get_prop_val(cur_child, "name"), token)) {
                cur_node = cur_child;
                found_it = true;
                break;
            }
            cur_child = next_child(cur_child);
        }

        if (!found_it) {
            cur_node = NULL;
            goto out;
        }
    }

out:
    free(tofree);
    return cur_node;
}
""",
    """struct dtree_node *adt_find_node(struct dtree_node *root, const char *path) {
    struct dtree_node *cur_node, *cur_child;
    gchar **tokens;

    tokens = g_strsplit(path, kDTPathNameSeparator, -1);
    cur_node = root;

    for (size_t token_index = 0; tokens[token_index] != NULL; token_index++) {
        const char *token = tokens[token_index];
        bool found_it = false;

        cur_child = first_child(cur_node);
        for (size_t i = 0; i < cur_node->nChildren; i++) {
            if (0 == strcmp(adt_get_prop_val(cur_child, "name"), token)) {
                cur_node = cur_child;
                found_it = true;
                break;
            }
            cur_child = next_child(cur_child);
        }

        if (!found_it) {
            cur_node = NULL;
            break;
        }
    }

    g_strfreev(tokens);
    return cur_node;
}
""",
)

replace_exact(
    "hw/arm/apple_regs.c",
    "#define TAG_OFFSET_EL2_LOCK            BIT(63)\n",
    "#define TAG_OFFSET_EL2_LOCK            (UINT64_C(1) << 63)\n",
)

print("Windows portability transformations applied successfully.")
