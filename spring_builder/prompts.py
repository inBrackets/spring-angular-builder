def prompt_single_select(label, options, default_id=None):
    """Prompt user to pick one option from a list."""
    print(f"\n{label}:")
    for i, opt in enumerate(options, 1):
        marker = " (default)" if opt["id"] == default_id else ""
        print(f"  {i}. {opt['name']}{marker}")

    while True:
        raw = input(f"Choose [1-{len(options)}] (enter for default): ").strip()
        if raw == "" and default_id is not None:
            return default_id
        try:
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]["id"]
        except ValueError:
            pass
        print("Invalid choice, try again.")


def prompt_yes_no(label, default=True):
    """Prompt for a yes/no question."""
    suffix = " [Y/n]" if default else " [y/N]"
    raw = input(f"\n{label}{suffix}: ").strip().lower()
    if raw == "":
        return default
    return raw in ("y", "yes")


def prompt_text(label, default=""):
    """Prompt for free-text input with a default."""
    suffix = f" [{default}]" if default else ""
    raw = input(f"\n{label}{suffix}: ").strip()
    return raw if raw else default


def prompt_dependencies(dep_groups):
    """Let user pick dependencies from categorized lists."""
    selected = []
    print("\n--- Dependencies ---")
    print("Browse categories and pick dependencies. Enter 'done' when finished.\n")

    categories = list(dep_groups)

    while True:
        print("\nCategories:")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat['name']}")
        print(f"  0. Done selecting dependencies")

        if selected:
            print(f"\nCurrently selected: {', '.join(selected)}")

        raw = input("Pick a category [0 to finish]: ").strip()
        if raw == "0" or raw.lower() == "done":
            break
        try:
            cat_idx = int(raw)
            if 1 <= cat_idx <= len(categories):
                cat = categories[cat_idx - 1]
                print(f"\n  {cat['name']}:")
                deps = cat["values"]
                for j, dep in enumerate(deps, 1):
                    check = "[x]" if dep["id"] in selected else "[ ]"
                    desc = dep.get("description", "")
                    desc_str = f" - {desc}" if desc else ""
                    print(f"    {j}. {check} {dep['name']}{desc_str}")
                print(f"    0. Back")

                while True:
                    dep_raw = input("  Toggle dependency # (0 to go back): ").strip()
                    if dep_raw == "0":
                        break
                    try:
                        dep_idx = int(dep_raw)
                        if 1 <= dep_idx <= len(deps):
                            dep_id = deps[dep_idx - 1]["id"]
                            if dep_id in selected:
                                selected.remove(dep_id)
                                print(f"    Removed: {deps[dep_idx - 1]['name']}")
                            else:
                                selected.append(dep_id)
                                print(f"    Added: {deps[dep_idx - 1]['name']}")
                        else:
                            print("    Invalid number.")
                    except ValueError:
                        print("    Invalid input.")
            else:
                print("Invalid category number.")
        except ValueError:
            print("Invalid input.")

    return selected
