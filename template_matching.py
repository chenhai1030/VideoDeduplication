
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from glob import glob
from winnow.feature_extraction.extraction_routine import load_featurizer
from winnow.feature_extraction.utils import load_image,load_video
class SearchEngine:
    def __init__(self,templates_root,library_glob,model):
        
        self.templates_root = templates_root
        self.library_glob = library_glob
        self.model = model
        self.available_queries = self.find_available_templates()
        self.frame_summaries = glob(library_glob)
        self.template_cache = self.load_available_templates()
        self.results_cache = {}
        
        
    def find_available_templates(self):
    
        folders = glob(self.templates_root)
        available = dict(zip([x.split('/')[-1] for x in folders],folders))
        
        return available
    
    def load_templates(self,files):
        resized = np.array([load_image(x,224) for x in files])
        features = self.model.extract(resized,batch_sz=10)
        return features
    
    def load_available_templates(self):
        
        cache = dict()
        
        for k,v in self.available_queries.items():
            
            cache[k] = self.load_templates(glob(v + '/**'))
            
        return cache
        
        
    def digest(self):
        pass
    
    
    def find(self,query,threshold=0.07,plot=True):
        
        feats = self.template_cache[query]
        print('Loaded query embeddings',feats.shape)
        self.results_cache[query] = dict()
        for i in range(len(self.frame_summaries)):
            try:
                video_summary = self.frame_summaries[i]
                sample = np.load(video_summary)
                video_frames = np.load(video_summary.replace('features','frames'))
                
                distances = np.mean(cdist(feats,sample,metric='cosine'),axis=0)
                self.results_cache[query][video_summary] = distances
                min_d = min(distances)
                
                
                if (min_d < threshold) and plot:
                    print('Minimum distance:{}'.format(min_d))
                    frame_of_interest = np.hstack(video_frames[np.argmin(distances):][:5])

                    plt.figure(figsize=(20,10))
                    plt.imshow(frame_of_interest)
                    plt.show()
            except:
                pass


def search_from_features(feats,threshold=0.07):
    for i in range(len(frame_summaries)):
    #     random = np.random.randint(0,len(frame_summaries))
        try:
            video_summary = frame_summaries[i]
            sample = np.load(video_summary)
            video_frames = np.load(video_summary.replace('features','frames'))

            distances = np.mean(cdist(feats,sample,metric='cosine'),axis=0)
            min_d = min(distances)

            
            if min_d < threshold:
                print('Minimum distance:{}'.format(min_d))
                frame_of_interest = np.hstack(video_frames[np.argmin(distances):][:5])

                plt.figure(figsize=(20,10))
                plt.imshow(frame_of_interest)
                plt.show()
        except Exception as e:
#             print(e)
            pass