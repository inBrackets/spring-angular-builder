import sys
from spring_builder.api import fetch_metadata, download_project, normalize_boot_version
from spring_builder.prompts import prompt_single_select, prompt_text, prompt_dependencies, prompt_yes_no
from spring_builder.angular import generate_angular_frontend
from spring_builder.project import extract_project, build_and_test, generate_github_actions


def main():
    print("=" * 60)
    print("  Spring Boot + Angular Project Generator")
    print("  (powered by start.spring.io)")
    print("=" * 60)

    print("\nFetching available options from Spring Initializr...")
    metadata = fetch_metadata()

    # --- Project type ---
    type_options = [
        t for t in metadata["type"]["values"]
        if t["id"] in ("maven-project", "gradle-project", "gradle-project-kotlin")
    ]
    type_default = metadata["type"]["default"]
    project_type = prompt_single_select("Project Type", type_options, type_default)

    # --- Language ---
    lang_options = metadata["language"]["values"]
    lang_default = metadata["language"]["default"]
    language = prompt_single_select("Language", lang_options, lang_default)

    # --- Spring Boot version ---
    boot_options = metadata["bootVersion"]["values"]
    boot_default = metadata["bootVersion"]["default"]
    boot_version = prompt_single_select("Spring Boot Version", boot_options, boot_default)
    if "SNAPSHOT" in boot_version or ".M" in boot_version:
        print("  ** Note: non-release versions may require snapshot/milestone repositories **")

    # --- Packaging ---
    pkg_options = metadata["packaging"]["values"]
    pkg_default = metadata["packaging"]["default"]
    packaging = prompt_single_select("Packaging", pkg_options, pkg_default)

    # --- Java version ---
    java_options = metadata["javaVersion"]["values"]
    java_default = metadata["javaVersion"]["default"]
    java_version = prompt_single_select("Java Version", java_options, java_default)

    # --- Project metadata (text fields) ---
    group_id = prompt_text("Group ID", metadata["groupId"].get("default", "com.example"))
    artifact_id = prompt_text("Artifact ID", metadata["artifactId"].get("default", "spring-angular-builder-output"))
    name = prompt_text("Project Name", artifact_id)
    description = prompt_text("Description", metadata["description"].get("default", "Demo project for Spring Boot"))
    package_name = prompt_text("Package Name", f"{group_id}.{artifact_id}")
    version = prompt_text("Version", metadata["version"].get("default", "0.0.1-SNAPSHOT"))

    # --- Dependencies ---
    dep_groups = metadata["dependencies"]["values"]
    dependencies = prompt_dependencies(dep_groups)

    # --- Angular frontend ---
    angular = prompt_yes_no("Include Angular frontend")

    # --- Output directory ---
    output_dir = prompt_text("Output directory", "spring-angular-builder-output")

    # --- Summary ---
    print(f"\n{'='*60}")
    print("  Project Summary")
    print(f"{'='*60}")
    print(f"  Type:          {project_type}")
    print(f"  Language:       {language}")
    print(f"  Boot Version:  {boot_version}")
    print(f"  Packaging:     {packaging}")
    print(f"  Java Version:  {java_version}")
    print(f"  Group:         {group_id}")
    print(f"  Artifact:      {artifact_id}")
    print(f"  Name:          {name}")
    print(f"  Description:   {description}")
    print(f"  Package:       {package_name}")
    print(f"  Version:       {version}")
    print(f"  Dependencies:  {', '.join(dependencies) if dependencies else 'none'}")
    print(f"  Angular:       {'yes' if angular else 'no'}")
    print(f"  Output:        {output_dir}")
    print(f"{'='*60}")

    confirm = input("\nGenerate project? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("Aborted.")
        sys.exit(0)

    # --- Build request parameters ---
    boot_version = normalize_boot_version(boot_version)
    params = {
        "type": project_type,
        "language": language,
        "bootVersion": boot_version,
        "packaging": packaging,
        "javaVersion": java_version,
        "groupId": group_id,
        "artifactId": artifact_id,
        "name": name,
        "description": description,
        "packageName": package_name,
        "version": version,
    }
    if dependencies:
        params["dependencies"] = ",".join(dependencies)

    # --- Download & extract ---
    zip_data = download_project(params)
    extract_project(zip_data, output_dir)

    # --- Generate Angular frontend ---
    if angular:
        generate_angular_frontend(output_dir, project_type)

    # --- Build & test ---
    build_and_test(output_dir, project_type)

    # --- Generate CI workflow ---
    generate_github_actions(output_dir, project_type, java_version, angular=angular)


if __name__ == "__main__":
    main()
