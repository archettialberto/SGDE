import numpy as np

def metadata_extraction(
    data, 
    labels=None, 
    epochs=epochs,
    batch_size=batch_size,
    conditioned=True, 
    data_format='image', 
    model_size='medium', 
    task='classification',
    padding=False
):
    """
    -1: error
    """
    metadata = {}   
    metadata['shape'] = data.shape
    
    if data_format == 'image':
        metadata['data_format'] = 'image'
        if len(data.shape)>4 or len(data.shape)<3:
            print(f'ABORT: {data.shape} is not a proper shape for an image dataset')
            return -1
        elif len(data.shape)==3:
            metadata['shape'] = data.shape + (1,)
            metadata['expand_shape'] = True
        else:
            metadata['expand_shape'] = False
    else:
        return -1
            
    if conditioned:
        assert len(data) == len(labels)
        assert len(labels.shape) == 1 or (len(labels.shape) == 2 and labels.shape[1] == 1)
        metadata['conditioned'] = True
        metadata['labels_shape'] = labels.shape
        if task == 'classification':
            metadata['task'] = 'classification'
            metadata['classes'] = np.unique(labels)
            metadata['num_classes'] = len(np.unique(labels))
        else:
            metadata['task'] = None
        
    else:
        metadata['conditioned'] = False
        metadata['task'] = None
        
    
    # Model section
        
    metadata['model_size'] = model_size
    metadata['epochs'] = epochs
    metadata['batch_size'] = batch_size
    metadata['padding'] = padding # Implementare logica di padding rispetto alla profondità massima    
    metadata['max_blocks'] = 2 # Implementare logica per il calcolo della dimensione massima
    
    metadata['leraning_rate'] = 1e-4
    metadata['discriminator_rounds'] = 3
    
    if model_size == 'medium':
        metadata['blocks'] = min(2, metadata['max_blocks'])
        metadata['filters'] = 64
        metadata['embedding_dim'] = 64
        metadata['latent_dim'] = 128
    
    return metadata