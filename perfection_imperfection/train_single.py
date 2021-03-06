"""
# author: lvwanyou
# file: train.py
"""

import argparse
import os
import time

import torch
import torchvision
from torch import nn, optim
from torchvision import transforms

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# /ANIMALS/cat_dogs
parser = argparse.ArgumentParser("""Image classifical!""")
# '../', 获取当前脚本所在路径的上一级路径
parser.add_argument('--path', type=str, default='./data/Products/perfection_imperfection/',
                    help="""image dir path default: './data/Products/perfection_imperfection/'.""")
parser.add_argument('--epochs', type=int, default=10,
                    help="""Epoch default:10.""")
parser.add_argument('--batch_size', type=int, default=128,
                    help="""Batch_size default:128.""")
parser.add_argument('--lr', type=float, default=1e-4,
                    help="""learning_rate. Default=1e-4""")
parser.add_argument('--num_classes', type=int, default=2,
                    help="""num classes. Default: 2.""")
parser.add_argument('--model_path', type=str, default='./models/pytorch/Products/perfection_imperfection/',
                    help="""Save model path""")
parser.add_argument('--model_name', type=str, default='SinglePerfectionImperfection.pth',
                    help="""Model name.""")
parser.add_argument('--display_epoch', type=int, default=1)

args = parser.parse_args()

# Create model
if not os.path.exists(args.model_path):
    os.makedirs(args.model_path)

transform = transforms.Compose([
    transforms.Resize(128),  # 将图像转化为800 * 800
    transforms.RandomHorizontalFlip(p=0.75),  # 有0.75的几率随机旋转
    transforms.RandomCrop(114),  # 从图像中裁剪一个24 * 24的
    transforms.ToTensor(),  # 将numpy数据类型转化为Tensor
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) # 归一化
    # transforms.TenCrop
])

path2 = os.path.abspath('./data/')
print("=======    " + path2)

# Load data

train_datasets = torchvision.datasets.ImageFolder(root=args.path + 'train_single/',
                                                  transform=transform)
# torchvision.datasets.ImageFolder只是返回list，list是不能作为模型输入的，因此在PyTorch中需要用另一个类来封装list，
# 那就是：torch.utils.data.DataLoader
train_loader = torch.utils.data.DataLoader(dataset=train_datasets,
                                           batch_size=args.batch_size,
                                           shuffle=True)

test_datasets = torchvision.datasets.ImageFolder(root=args.path + 'test_single/',
                                                 transform=transform)

test_loader = torch.utils.data.DataLoader(dataset=train_datasets,
                                          batch_size=args.batch_size,
                                          shuffle=True)


def main():
    print(f"Train numbers:{len(train_datasets)}")

    # create module in the first time
    model = torchvision.models.resnet18(pretrained=True).to(device)  # 导入 ResNet18网络作为模型
    model.avgpool = nn.AvgPool2d(4, 1).to(device)

    model.fc = nn.Linear(512, args.num_classes).to(device)

    # Load model in the future.
    # if torch.cuda.is_available():
    #     model = torch.load(args.model_path + args.model_name).to(device)
    # else:
    #     model = torch.load(args.model_path + args.model_name, map_location='cpu')

    print(model)

    # cast
    cast = nn.CrossEntropyLoss().to(device)
    # Optimization
    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-8)

    for epoch in range(1, args.epochs + 1):
        model.train()
        # start time
        start = time.time()
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            # Forward pass
            outputs = model(images)
            loss = cast(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()  # 先将网络中的所有梯度置0
            loss.backward()
            optimizer.step()

        if epoch % args.display_epoch == 0:
            end = time.time()
            print(f"Epoch [{epoch}/{args.epochs}], "
                  f"Loss: {loss.item():.8f}, "
                  f"Time: {(end-start) * args.display_epoch:.1f}sec!")

            model.eval()    # Sets the module in evaluation mode.

            correct_prediction = 0.
            total = 0
            for images, labels in test_loader:
                # to GPU
                images = images.to(device)
                labels = labels.to(device)
                # print prediction
                outputs = model(images)
                # equal prediction and acc
                _, predicted = torch.max(outputs.data, 1)
                # val_loader total
                total += labels.size(0)
                # add correct
                correct_prediction += (predicted == labels).sum().item()

            print(f"Acc: {(correct_prediction / total):4f}")

        # Save the model checkpoint
        torch.save(model, args.model_path + args.model_name)
    print(f"Model save to {args.model_path + args.model_name}.")


if __name__ == '__main__':
    main()
