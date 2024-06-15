from deepface import DeepFace
# dfs = DeepFace.find(
#   img_path = "uploads//0006_01.jpg",
#   db_path = "cvdb",
#   enforce_detection=False
# )
# similar_images = []
# for df in dfs:
#    similar_images.extend(df['identity'].tolist())
# verification = DeepFace.verify(img1_path = "cvdb//n000001//0001_01.jpg", img2_path = "cvdb//n000029//0002_01.jpg")
# print(verification)
analysis = DeepFace.analyze(img_path="uploads\\0001_01.jpg", actions=["age", "gender", "emotion", "race"], enforce_detection=False)
print(analysis)
