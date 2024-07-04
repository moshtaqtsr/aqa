
**AQA (Assembly Quality Assessment)**

This code is designed to assess the quality of genome assemblies. It can be easily customized for different species and other genomic analyses.

The tool is particularly useful for ensuring genome assemblies meet quality standards, allowing users to define ranges for genome size, GC content, and the maximum number of contigs.

**Installation Instructions:**

1. Clone the `install_aqa.sh` script from the following link:
   ```
   https://github.com/moshtaqtsr/aqa/blob/main/notebook/install_aqa.sh
   ```

2. Make the script executable:
   ```
   chmod +x install_aqa.sh
   ```

3. Execute the script:
   ```
   ./install_aqa.sh
   ```

4. Verify Installation:
   ```
   aqa --help
   ```

If any required libraries are missing, you will receive a notification. You can easily install them using:
   ```
   pip install <library_name>
   ```

**Usage:**

Navigate to the directory containing your genome assemblies, then run:

```
aqa
```
This will analyze the assemblies without specifying cutoffs and will not produce plots.

Alternatively, specify cutoffs for analysis:
```
aqa --con-cut 400 --size_min 2800000 --size_max 3600000 --gc_min 36.6 --gc_max 37.6
```


## API Reference

#### Get all items

```http
  GET /api/items
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

#### Get item

```http
  GET /api/items/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |

#### add(num1, num2)

Takes two numbers and returns the sum.


## Authors

- @moshtaqtsr


