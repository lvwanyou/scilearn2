"""
# author: lvwanyou
"""

import argparse
import os

import torch
import torchvision
from torchvision import transforms

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

parser = argparse.ArgumentParser("""Image classifical!""")
parser.add_argument('--path', type=str, default='./data/Products/perfection_imperfection/',
                    help="""image dir path default: './data/Products/perfection_imperfection/'.""")
parser.add_argument('--batch_size', type=int, default=256,
                    help="""Batch_size default:154.""")
parser.add_argument('--num_classes', type=int, default=2,
                    help="""num classes""")
parser.add_argument('--model_path', type=str, default='./models/pytorch/Products/perfection_imperfection/',
                    help="""Save model path""")
parser.add_argument('--model_name', type=str, default='PerfectionImperfection.pth',
                    help="""Model name.""")

args = parser.parse_args()

# Create model
if not os.path.exists(args.model_path):
    os.makedirs(args.model_path)

transform = transforms.Compose([
    transforms.Resize(128),  # 将图像转化为128 * 128
    transforms.RandomCrop(114),  # 从图像中裁剪一个114 * 114的
    transforms.ToTensor(),  # 将numpy数据类型转化为Tensor
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),  # 归一化
])

# Load data
test_datasets = torchvision.datasets.ImageFolder(root=args.path + 'val/',
                                                 transform=transform)


test_loader = torch.utils.data.DataLoader(dataset=test_datasets,
                                          batch_size=args.batch_size,
                                          shuffle=True)

# train_datasets zip
item = test_datasets.class_to_idx
def main():
    print(f"total test numbers: {len(test_datasets)}.")
    # Load model
    if torch.cuda.is_available():
        model = torch.load(args.model_path + args.model_name).to(device)
    else:
        model = torch.load(args.model_path + args.model_name, map_location='cpu')
    model.eval()

    correct = 0.
    total = 0
    for images, labels in test_loader:
        # to GPU
        images = images.to(device)
        labels = labels.to(device)
        # print prediction
        outputs = model(images)
        # equal prediction and acc
        _, predicted = torch.max(outputs.data, 1)

        print(f"label kind:{labels}")           # 0:cat;  1:dog       # 0:imperfections ;  1:perfection

        print(f"predicted kind:{predicted}")
        for i in range(len(predicted)):
            file = str(test_datasets.imgs[i])[2:-5]
            if int(predicted[i]) == 1:
                print(f"{i+1}.({file}) is perfection!")
            else:
                print(f"{i+1}.({file}) is imperfection!")
        # val_loader total
        total += labels.size(0)
        # add correct
        correct += (predicted == labels).sum().item()

    print(f"Acc: {100 * correct / total:.4f}")


if __name__ == '__main__':
    main()
