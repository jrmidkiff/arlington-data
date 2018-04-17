## Interactive Use
Generate a pandas dataframe with the 100 most recent police incidents:

```python
from data_portal import Arlington

arva = Arlington()
frame = arva.police_incidents(100)
```
