# HEPData repo for stop combination

To pack all yaml files for submission:
```
tar -czvf submission.tgz *.yaml
```

Validate
```
hepdata-validate -a submission.tgz
```

Link to hepdata validation tools: [documentation](https://hepdata-validator.readthedocs.io/en/latest/#command-line)
