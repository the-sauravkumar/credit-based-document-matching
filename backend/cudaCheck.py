import torch
print(torch.cuda.memory_allocated())  # Should show non-zero if in use
print(torch.cuda.memory_reserved())   # Should show GPU memory reserved
