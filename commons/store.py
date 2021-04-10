import os
import pandas as pd
import numpy as np
import itertools
import pickle


class PickleStore(object):
    """Storage object to read and write very large dataset as pickle file"""
    
    def __init__(self, fname):
        self.fname = fname
    
    def write(self, dataset, chunksize=500):
        """Write dataset in chunks to pickle"""
        total = len(dataset)
        step = chunksize
        n = total // chunksize
        
        iterator = (itertools.count(start = 0, step = step))
        
        with open(self.fname, 'wb') as f:
            print(f'Saving {self.fname} ...')
            
            for i in (next(iterator) for _ in range(n+1)):
                end = i + step
                if end > total:
                    end = total

                if isinstance(dataset, (list, np.ndarray)):
                    pickle.dump(dataset[i:end], f, pickle.HIGHEST_PROTOCOL)
                elif isinstance(dataset, pd.DataFrame):
                    pickle.dump(dataset.iloc[i:end], f, pickle.HIGHEST_PROTOCOL)
                else:
                    raise TypeError('Only list, numpy array, and pandas DataFrame are supported')
                
                print(f'\t... {end} records', end='\r')

            print('\nDone!!')
            
                        
    def load(self, asPandasDF=False, columns=None):
        """Load pickle in chunks"""
        results = []
        with open(self.fname, 'rb') as f:
            print(f'Loading {self.fname} ...')
            while True:
                try:
                    results.extend(pickle.load(f))
                    print(f'\t... {len(results)} records', end='\r')
                except EOFError:
                    print('\nDone!!')
                    break
        
        if asPandasDF:
            if columns is None:
                raise TypeError('Columns can not be None')
            
            return pd.DataFrame.from_records(results, columns=columns)
            
        return results


class NpyStore(object):
    """Storage object to read and write very large dataset as npy file"""
    
    def __init__(self, fname):
        self.fname = fname
    
    
    def write(self, dataset, chunksize=500):
        
        total = len(dataset)
        step = chunksize
        n = total // chunksize
        
        iterator = (itertools.count(start = 0, step = step))
        
        with open(self.fname, 'ab') as f:
            print(f'Saving {self.fname} ...')
            
            for i in (next(iterator) for _ in range(n+1)):
                end = i + step
                if end > total:
                    end = total

                if isinstance(dataset, (list, np.ndarray)):
                    np.save(f, dataset[i:end])
                else:
                    raise TypeError('Only list and numpy array are supported')
                
                print(f'\t... {end} records', end='\r')

            print('\nDone!!')
   
    def load(self, axis=0):
        
        results = []
        
        with open(self.fname, "rb") as f:
            print(f'Loading {self.fname} ...')
            
            fsz = os.fstat(f.fileno()).st_size
            results = np.load(f, allow_pickle=True)
            while f.tell() < fsz:
                results = np.concatenate((results, np.load(f, allow_pickle=True)), axis=axis)
                print(f'\t... {len(results)} records', end='\r')
              
        print('\nDone!!')       
        return results;
    
    @property
    def header(self):
        """Read the header of the npy file"""

        with open(self.fname, 'rb') as f:
            version = np.lib.format.read_magic(f)
            shape, fortran, dtype = np.lib.format._read_array_header(f, version)
        
        return version, {'descr': dtype,
                         'fortran_order' : fortran,
                         'shape' : shape}
                
                
                
                
        