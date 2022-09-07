import torch

def list2tensor(x):
    x_stacked = torch.stack(x, dim=0)
    return x_stacked.type(torch.FloatTensor)

def sim_matrix(a, b, eps=1e-8):
    """
    added eps for numerical stability
    """
    a_n, b_n = a.norm(dim=1)[:, None], b.norm(dim=1)[:, None]
    a_norm = a / torch.max(a_n, eps * torch.ones_like(a_n))
    b_norm = b / torch.max(b_n, eps * torch.ones_like(b_n))
    sim_mt = torch.mm(a_norm, b_norm.transpose(0, 1))
    return sim_mt

def file_metric_asym(a,b):
    diff_mat = 1 - sim_matrix(a,b)
    min_tensor = torch.min(diff_mat, dim=1)[0]
    sq_tensor = min_tensor ** 2
    sum_sq_tensor =  torch.sum(sq_tensor)
    # sqrt_tensor = torch.sqrt(sum_sq_tensor)
    return sum_sq_tensor
    
def file_metric(a,b):
    at = list2tensor(a)
    bt = list2tensor(b)
    return file_metric_asym(at,bt) + file_metric_asym(bt,at)
