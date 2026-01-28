# How to add a new plugin

## 📌 Overview

Plugins in Synaptomancer allow you to extend the signal processing pipeline
by adding custom processing, feature extraction, or classification steps.

Each plugin is composed of:
- A **UI interface** for user-configurable parameters
- A **method implementation** used during pipeline execution

## 📂 Plugin Structure

Each plugin must follow this structure:

```text
plugin_name/
├── interface.py
└── method.py
```

## 🧠 PluginInterface Class

All plugins must provide an interface class.

This class is responsible for defining the user interface (UI) that allows
users to configure the plugin hyperparameters.

The interface uses PyQt6 widgets such as:


- `QLineEdit`

- `QComboBox`

- `QCheckBox`

### Example use case

For example, when creating a plugin that wraps
`sklearn.neighbors.KNeighborsClassifier`, you may want to expose the
`n_neighbors` hyperparameter so the user can modify it via the UI.

> ⚠️ Creating interfaces requires basic knowledge of PyQt6.

## 🛠️ PluginMethod Class

All plugins must provide a method class.

This class contains the actual processing logic and can either:

- Implement a custom method

- Wrap an existing method using inheritance

### 🔁 Using Inheritance (Recommended)

The easiest way to create a plugin method is to inherit from an existing
scikit-learn class (or compatible).

```python
from sklearn.neighbors import KNeighborsClassifier

class PluginMethod(KNeighborsClassifier):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs
```

This structure is sufficient for the plugin to be executed correctly
inside the Synaptomancer pipeline.

### 🧩 Creating your own method

Synaptomancer follows the scikit-learn pipeline logic:

https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline. 

Therefore, any custom method must implement the following methods:

- `fit`

- `transform`

- `predict`

⚠️ Any class that does not implement this interface may fail during
pipeline execution.