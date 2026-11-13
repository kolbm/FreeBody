"""Bounded undo/redo of source diagrams; calculated output never becomes manual input."""
import copy
class ProjectHistory:
    def __init__(self,project,limit=30):
        self.present=copy.deepcopy(project);self.past=[];self.future=[];self.limit=limit
    def record(self,project):
        if project==self.present:return
        self.past.append(self.present);self.past=self.past[-self.limit:]
        self.present=copy.deepcopy(project);self.future=[]
    def undo(self):
        if self.past:
            self.future.append(self.present);self.present=self.past.pop()
        return copy.deepcopy(self.present)
    def redo(self):
        if self.future:
            self.past.append(self.present);self.present=self.future.pop()
        return copy.deepcopy(self.present)
