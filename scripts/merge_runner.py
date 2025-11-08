from core import FileMerger, FileSimilarity

merger = FileMerger(root_folder="./sample_files")
merger.scan_files([".txt"])
merger.auto_group()

for group in merger.groups:
    suggestions = FileSimilarity.suggest_pairs(group.files, threshold=0.6)
    print(suggestions)
