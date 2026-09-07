# Data and redistribution

The training run used 9,710 rows and 576 validation rows. Full row-level training and validation files are intentionally not distributed in v0.2 Alpha.

Sources and transformations included:

- Tatoeba/ManyThings Chinese-English parallel sentences, carrying CC BY 2.0 attribution and source-specific terms.
- CC-CEDICT-derived lexical mapping logic, whose dictionary source is CC BY-SA 4.0.
- Reviewed synthetic teacher examples produced for this project using Luna, plus controller review and corrections.
- Programmatically generated lexical-rescue variants and typo perturbations.
- Small general-instruction replay and English-identity examples used to reduce capability loss.

The mixed corpus contains records with different provenance and license obligations. The project does not claim that applying one repository-wide license would make every source row freely redistributable. Consequently, v0.2 publishes the aggregate manifest, attribution, generation/cleaning scripts, frozen evaluation, and reviewed outputs, but withholds the complete training and validation JSONL files.

The frozen evaluation is published for reproducibility. It is project-authored, consists of 100 WordStitch examples plus small retention sets, and was reviewed by Astra rather than independent human evaluators.

