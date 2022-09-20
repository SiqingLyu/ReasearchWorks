'''
nad, fwd, bwd network
refer to PSMN
1. TLCNet: 采用 3D CNN
2. TLCNetU: 采用Unet的结构作为后端
'''

from __future__ import print_function
from models.submodule import *
from models.utils import unetUpsimple, unetConv2, unetUp, unetUpC, unetUpCC


class hourglass(nn.Module):
    def __init__(self, inplanes):
        super(hourglass, self).__init__()

        self.conv1 = nn.Sequential(convbn_3d(inplanes, inplanes * 2, kernel_size=3, stride=2, pad=1),
                                   nn.ReLU(inplace=True))

        self.conv2 = convbn_3d(inplanes * 2, inplanes * 2, kernel_size=3, stride=1, pad=1)

        self.conv3 = nn.Sequential(convbn_3d(inplanes * 2, inplanes * 2, kernel_size=3, stride=2, pad=1),
                                   nn.ReLU(inplace=True))

        self.conv4 = nn.Sequential(convbn_3d(inplanes * 2, inplanes * 2, kernel_size=3, stride=1, pad=1),
                                   nn.ReLU(inplace=True))

        self.conv5 = nn.Sequential(
            nn.ConvTranspose3d(inplanes * 2, inplanes * 2, kernel_size=3, padding=1, output_padding=1, stride=2,
                               bias=False),
            nn.BatchNorm3d(inplanes * 2))  # +conv2

        self.conv6 = nn.Sequential(
            nn.ConvTranspose3d(inplanes * 2, inplanes, kernel_size=3, padding=1, output_padding=1, stride=2,
                               bias=False),
            nn.BatchNorm3d(inplanes))  # +x

    def forward(self, x, presqu, postsqu):

        out = self.conv1(x)  # in:1/4 out:1/8
        pre = self.conv2(out)  # in:1/8 out:1/8
        if postsqu is not None:
            pre = F.relu(pre + postsqu, inplace=True)
        else:
            pre = F.relu(pre, inplace=True)

        out = self.conv3(pre)  # in:1/8 out:1/16
        out = self.conv4(out)  # in:1/16 out:1/16

        if presqu is not None:
            post = F.relu(self.conv5(out) + presqu, inplace=True)  # in:1/16 out:1/8
        else:
            post = F.relu(self.conv5(out) + pre, inplace=True)

        out = self.conv6(post)  # in:1/8 out:1/4

        return out, pre, post


class Uencoder(nn.Module):
    def __init__(
        self, feature_scale=4, is_deconv=True, in_channels=3, is_batchnorm=True, filters = [64, 128, 256, 512, 1024]
    ):
        super(Uencoder, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale
        #filters = [int(x / self.feature_scale) for x in filters]
        # downsampling
        self.conv1 = unetConv2(self.in_channels, filters[0], self.is_batchnorm)
        self.maxpool1 = nn.MaxPool2d(kernel_size=2)

        self.conv2 = unetConv2(filters[0], filters[1], self.is_batchnorm)
        self.maxpool2 = nn.MaxPool2d(kernel_size=2)

        self.conv3 = unetConv2(filters[1], filters[2], self.is_batchnorm)
        self.maxpool3 = nn.MaxPool2d(kernel_size=2)

        self.conv4 = unetConv2(filters[2], filters[3], self.is_batchnorm)
        self.maxpool4 = nn.MaxPool2d(kernel_size=2)

        self.center = unetConv2(filters[3], filters[4], self.is_batchnorm)

    def forward(self, inputs):
        # inputs
        conv1 = self.conv1(inputs)
        maxpool1 = self.maxpool1(conv1)

        conv2 = self.conv2(maxpool1)
        maxpool2 = self.maxpool2(conv2)

        conv3 = self.conv3(maxpool2)
        maxpool3 = self.maxpool3(conv3)

        conv4 = self.conv4(maxpool3)
        maxpool4 = self.maxpool4(conv4)

        center = self.center(maxpool4)

        return conv1, conv2, conv3, conv4, center


class Udecoder(nn.Module):
    def __init__(self, feature_scale=4, n_classes=21, is_deconv=True, filters = [64, 128, 256, 512, 1024]):
        super(Udecoder, self).__init__()
        self.is_deconv = is_deconv
        self.feature_scale = feature_scale
        self.filters = filters
        # upsampling
        self.up_concat4 = unetUp(filters[4], filters[3], self.is_deconv)
        self.up_concat3 = unetUp(filters[3], filters[2], self.is_deconv)
        self.up_concat2 = unetUp(filters[2], filters[1], self.is_deconv)
        self.up_concat1 = unetUp(filters[1], filters[0], self.is_deconv)

        # final conv (without any concat)
        self.final = nn.Conv2d(filters[0], n_classes, 1)

    def forward(self, conv1, conv2, conv3, conv4, center):
        up4 = self.up_concat4(conv4, center)
        up3 = self.up_concat3(conv3, up4)
        up2 = self.up_concat2(conv2, up3)
        up1 = self.up_concat1(conv1, up2)

        final = self.final(up1)

        return final


class UdecoderC(nn.Module):
    def __init__(self, feature_scale=4, n_classes=21, is_deconv=True, filters = [64, 128, 256, 512, 1024]):
        super(UdecoderC, self).__init__()
        self.is_deconv = is_deconv
        self.feature_scale = feature_scale
        self.filters = filters
        # upsampling
        self.up_concat4 = unetUpC(filters[4], filters[3], self.is_deconv)
        self.up_concat3 = unetUp(filters[3], filters[2], self.is_deconv)
        self.up_concat2 = unetUp(filters[2], filters[1], self.is_deconv)
        self.up_concat1 = unetUp(filters[1], filters[0], self.is_deconv)

        # final conv (without any concat)
        self.final = nn.Conv2d(filters[0], n_classes, 1)

    def forward(self, conv1, conv2, conv3, conv4, center):
        up4 = self.up_concat4(conv4, center)
        up3 = self.up_concat3(conv3, up4)
        up2 = self.up_concat2(conv2, up3)
        up1 = self.up_concat1(conv1, up2)

        final = self.final(up1)

        return final


class UdecoderCC(nn.Module):
    def __init__(self, feature_scale=4, n_classes=21, is_deconv=True, filters = [64, 128, 256, 512, 1024]):
        super(UdecoderCC, self).__init__()
        self.is_deconv = is_deconv
        self.feature_scale = feature_scale
        self.filters = filters
        # upsampling
        self.up_concat4 = unetUpCC(filters[4], filters[3], self.is_deconv)
        self.up_concat3 = unetUp(filters[3], filters[2], self.is_deconv)
        self.up_concat2 = unetUp(filters[2], filters[1], self.is_deconv)
        self.up_concat1 = unetUp(filters[1], filters[0], self.is_deconv)

        # final conv (without any concat)
        self.final = nn.Conv2d(filters[0], n_classes, 1)

    def forward(self, conv1, conv2, conv3, conv4, center):
        up4 = self.up_concat4(conv4, center)
        up3 = self.up_concat3(conv3, up4)
        up2 = self.up_concat2(conv2, up3)
        up1 = self.up_concat1(conv1, up2)

        final = self.final(up1)

        return final


class SSNVVHNetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(SSNVVHNetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 4:8, :, :]) # ssn
        conv20, conv21, conv22, conv23, center2 = self.uencoder2(inputs[:, :4, :, :]) # mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        com_center = torch.cat([center2, center1], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center) # ssn height
        final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        final4 = self.final(torch.cat([final1, final2, final3], 1)) # ssn_vvh+mux height

        # deep supervision
        if self.training:
            return final1, final2, final3, final4
        else:
            return final4, final3


class VVHNetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(VVHNetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(2, n_classes, 1) #  height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 4:8, :, :]) # ssn
        conv20, conv21, conv22, conv23, center2 = self.uencoder2(inputs[:, :4, :, :]) # mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center2, center1], 1)
        # final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center) # ssn height
        final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        final4 = self.final(torch.cat([final2, final3], 1)) # ssn_vvh+mux height

        # deep supervision
        if self.training:
            return final2, final3, final4
        else:
            return final4, final3

class VVHNetU_withfootprint(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(VVHNetU_withfootprint, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(2, n_classes, 1) #  height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 5:9, :, :])  # ssn
        conv20, conv21, conv22, conv23, center2 = self.uencoder2(inputs[:, 1:5, :, :])  # mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 9:, :, :])  # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, :1, :, :])  # footprint

        # decoder 1 & 2 & 3
        com_center = torch.cat([center2, center4], 1)
        # final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center)  # ssn height
        final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2)  # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3)  # vvh height
        final4 = self.final(torch.cat([final2, final3], 1))  # ssn_vvh+mux height

        # deep supervision
        if self.training:
            return final2, final3, final4
        else:
            return final4, final3


class ALL_VVHNetU_withfootprint(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVHNetU_withfootprint, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        # filters = [16, 32, 64, 128, 256]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels+4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(2, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 1:9, :, :]) # ssn+mux
        # conv20, conv21, conv22, conv23, center2 = self.uencoder2(inputs[:, 1:9, :, :]) # mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 9:, :, :]) # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, :1, :, :]) # footprint

        # decoder 1 & 2 & 3
        com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        final4 = self.final(torch.cat([final1,  final3], 1)) # ssn + vvh + mux height

        # deep supervision
        if self.training:
            return final1,  final3, final4
        else:
            return final4, final3


class ALL_VVHNetU_concatfootprint(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVHNetU_withfootprint, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        # filters = [16, 32, 64, 128, 256]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels+4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 1:9, :, :]) # ssn+mux
        # conv20, conv21, conv22, conv23, center2 = self.uencoder2(inputs[:, 1:9, :, :]) # mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 9:, :, :]) # vvh
        # conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, :1, :, :]) # footprint

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        final4 = self.final(torch.cat([final1,  final3, inputs[:, :1, :, :]], 1)) # ssn + vvh + mux height

        # deep supervision
        if self.training:
            return final1,  final3, final4
        else:
            return final4, final3


class ALL_VVHNetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVHNetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels+4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        # self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(2, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:8, :, :]) # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        final4 = self.final(torch.cat([final1,  final3], 1)) # ssn + vvh + mux height

        # deep supervision
        if self.training:
            return final1,  final3, final4
        else:
            return final4, final3


class ALL_VVH_DSMNetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVH_DSMNetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels+4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder4 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:8, :, :]) # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:9, :, :]) # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, 9:10, :, :]) # dsm or ndsm

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        final4 = self.udecoder4(conv40, conv41, conv42, conv43, center4) # dsm height
        final5 = self.final(torch.cat([final1,  final3, final4], 1)) # mux,ssn + vvh + dsm height

        # deep supervision
        if self.training:
            return final1,  final3, final4, final5
        else:
            return final5, final3, final4


class ALL_VVH_DSMDEMNetU(nn.Module):
    def __init__(
            self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVH_DSMDEMNetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels + 4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 1, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder4 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1)  # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:8, :, :])  # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:9, :, :])  # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, 9:12, :, :])  # dem dsm ndsm

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1)  # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3)  # vvh height
        final4 = self.udecoder4(conv40, conv41, conv42, conv43, center4)  # dsm height
        final5 = self.final(torch.cat([final1, final3, final4], 1))  # mux,ssn + vvh + dsm height

        # deep supervision
        if self.training:
            return final1, final3, final4, final5
        else:
            return final5, final3, final4


class ALL_VVH_DSMDEM_FPcattoendNetU(nn.Module):
    def __init__(
            self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVH_DSMDEM_FPcattoendNetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels + 4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 1, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder4 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(4, n_classes, 1)  # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 1:9, :, :])  # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 9:10, :, :])  # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, 10:13, :, :])  # dem dsm ndsm

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1)  # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3)  # vvh height
        final4 = self.udecoder4(conv40, conv41, conv42, conv43, center4)  # dsm height
        final5 = self.final(torch.cat([final1, final3, final4, inputs[:, :1, :, :]], 1))  # mux,ssn + vvh + dsm , FP height

        # deep supervision
        if self.training:
            return final1, final3, final4, final5
        else:
            return final5, final3, final4


class ALL_VVH_DSMDEM_catROAD_NetU(nn.Module):
    def __init__(
            self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVH_DSMDEM_catROAD_NetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels + 4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 1, self.is_batchnorm, filters)
        self.uencoder5 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)


        # upsampling
        self.udecoder1 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder4 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1)  # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:8, :, :])  # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:9, :, :])  # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, 9:12, :, :])  # dem dsm ndsm
        conv50, conv51, conv52, conv53, center5 = self.uencoder5(inputs[:, 12:13, :, :])  # road

        # decoder 1 & 2 & 3
        com_center = torch.cat([center1, center5], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center)  # ssn+mux+road height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3)  # vvh height
        final4 = self.udecoder4(conv40, conv41, conv42, conv43, center4)  # dsm height
        final5 = self.final(torch.cat([final1, final3, final4], 1))  # mux,ssn + vvh + dsm height

        # deep supervision
        if self.training:
            return final1, final3, final4, final5
        else:
            return final5, final3, final4


class ALL_VVH_DSMDEM_catROAD2_NetU(nn.Module):
    def __init__(
            self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVH_DSMDEM_catROAD2_NetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels + 4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 1, self.is_batchnorm, filters)
        self.uencoder5 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)


        # upsampling
        self.udecoder1 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder4 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1)  # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:8, :, :])  # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:9, :, :])  # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, 9:12, :, :])  # dem dsm ndsm
        conv50, conv51, conv52, conv53, center5 = self.uencoder5(inputs[:, 12:13, :, :])  # road

        # decoder 1 & 2 & 3
        com_center1 = torch.cat([center1, center5], 1)
        com_center3 = torch.cat([center3, center5], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center1)  # ssn+mux+road height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, com_center3)  # vvh height
        final4 = self.udecoder4(conv40, conv41, conv42, conv43, center4)  # dsm height
        final5 = self.final(torch.cat([final1, final3, final4], 1))  # mux,ssn + vvh + dsm height

        # deep supervision
        if self.training:
            return final1, final3, final4, final5
        else:
            return final5, final3, final4


class ALL_VVH_DSMDEM_catROAD3_NetU(nn.Module):
    def __init__(
            self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVH_DSMDEM_catROAD3_NetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels + 4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 1, self.is_batchnorm, filters)
        self.uencoder5 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)


        # upsampling
        self.udecoder1 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder4 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1)  # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:8, :, :])  # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:9, :, :])  # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, 9:12, :, :])  # dem dsm ndsm
        conv50, conv51, conv52, conv53, center5 = self.uencoder5(inputs[:, 12:13, :, :])  # road

        # decoder 1 & 2 & 3
        com_center1 = torch.cat([center1, center5], 1)
        com_center3 = torch.cat([center3, center5], 1)
        com_center4 = torch.cat([center4, center5], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center1)  # ssn+mux+road height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, com_center3)  # vvh height
        final4 = self.udecoder4(conv40, conv41, conv42, conv43, com_center4)  # dsm height
        final5 = self.final(torch.cat([final1, final3, final4], 1))  # mux,ssn + vvh + dsm height

        # deep supervision
        if self.training:
            return final1, final3, final4, final5
        else:
            return final5, final3, final4


class ALL_VVH_centercat_DSMDEMNetU(nn.Module):
    def __init__(
            self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(ALL_VVH_centercat_DSMDEMNetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels + 4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels - 1, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder4 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1)  # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:8, :, :])  # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:9, :, :])  # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, 9:12, :, :])  # dem dsm ndsm

        # decoder 1 & 2 & 3
        com_center = torch.cat([center3, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1)  # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, com_center)  # vvh height
        final4 = self.udecoder4(conv40, conv41, conv42, conv43, center4)  # dsm height
        final5 = self.final(torch.cat([final1, final3, final4], 1))  # mux,ssn + vvh + dsm height

        # deep supervision
        if self.training:
            return final1, final3, final4, final5
        else:
            return final5, final3, final4


class SAR_NetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(SAR_NetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels+4, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        # self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(2, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:8, :, :]) # ssn+mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        # final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        # final4 = self.final(torch.cat([final1,  final3], 1)) # ssn + vvh + mux height

        # deep supervision
        if self.training:
            return final3
        else:
            return final3


class MUXSSN_NetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(MUXSSN_NetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels+16, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        # self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        # self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(2, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:20, :, :]) # ssn+mux
        # conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        # final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        # final4 = self.final(torch.cat([final1,  final3], 1)) # ssn + vvh + mux height

        # deep supervision
        if self.training:
            return final1
        else:
            return final1


class MUX_NetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(MUX_NetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        # self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        # self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        # self.final = nn.Conv2d(2, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:4, :, :]) # ssn+mux
        # conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        # final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        # final4 = self.final(torch.cat([final1,  final3], 1)) # ssn + vvh + mux height

        # deep supervision
        if self.training:
            return final1
        else:
            return final1


class SSN_NetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(SSN_NetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        # self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels*4, self.is_batchnorm, filters) # 16_channel
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        # self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        # self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        # self.final = nn.Conv2d(2, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 4:8, :, :]) # ssn when season_mode is False
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:4, :, :]) # mux
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 4:20, :, :]) # ssn_16channel
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 4:8, :, :]) # spr
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 8:12, :, :]) # smr
        # conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 12:16, :, :]) # fal
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 16:20, :, :]) # wnt
        # conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        # final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        # final4 = self.final(torch.cat([final1,  final3], 1)) # ssn + vvh + mux height

        # deep supervision
        if self.training:
            return final1
        else:
            return final1


class MUXSSNSAR_NetU(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(MUXSSNSAR_NetU, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels+5, self.is_batchnorm, filters)
        # self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        # self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        # self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        # self.final = nn.Conv2d(2, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 0:9, :, :]) # ssn+mux+VVH
        # conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        # com_center = torch.cat([center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, center1) # ssn+mux height
        # final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        # final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        # final4 = self.final(torch.cat([final1,  final3], 1)) # ssn + vvh + mux height

        # deep supervision
        if self.training:
            return final1
        else:
            return final1


class SSNVVHNetU_withfootprint(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(SSNVVHNetU_withfootprint, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)
        self.uencoder4 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = UdecoderCC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 5:9, :, :]) # ssn
        conv20, conv21, conv22, conv23, center2 = self.uencoder2(inputs[:, 1:5, :, :]) # mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 9:, :, :]) # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder4(inputs[:, :1, :, :]) # footprint

        # decoder 1 & 2 & 3
        com_center = torch.cat([center2, center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center) # ssn height
        final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux height
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh height
        final4 = self.final(torch.cat([final1, final2, final3], 1)) # ssn_vvh+mux height

        # deep supervision
        if self.training:
            return final1, final2, final3, final4
        else:
            return final4, final3


class SSNVVHNetU_classify(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(SSNVVHNetU_classify, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = UdecoderC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3*n_classes, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 4:8, :, :]) # ssn
        conv20, conv21, conv22, conv23, center2 = self.uencoder2(inputs[:, :4, :, :]) # mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 8:, :, :]) # vvh

        # decoder 1 & 2 & 3
        com_center = torch.cat([center2, center1], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center) # ssn class
        final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux class
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh class
        final4 = self.final(torch.cat([final1, final2, final3], 1)) # ssn_vvh+mux height

        final1_class = F.softmax(final1,dim=1)
        final2_class = F.softmax(final2,dim=1)
        final4_class = F.softmax(final4,dim=1)
        final3_class = F.softmax(final3,dim=1)
        # deep supervision
        if self.training:
            return final1_class, final2_class, final3_class, final4_class
        else:
            return final4_class, final3_class


class SSNVVHNetU_classify_withfootprint(nn.Module):
    def __init__(
        self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=4, is_batchnorm=True
    ):
        super(SSNVVHNetU_classify_withfootprint, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        self.uencoder1 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder2 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels, self.is_batchnorm, filters)
        self.uencoder3 = Uencoder(self.feature_scale, self.is_deconv, self.in_channels-3, self.is_batchnorm, filters)

        # upsampling
        self.udecoder1 = UdecoderCC(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder2 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        self.udecoder3 = Udecoder(self.feature_scale, n_classes, self.is_deconv, filters)
        # final layer
        self.final = nn.Conv2d(3*n_classes, n_classes, 1) # height_tlc, height_mux, height_vvh

    def forward(self, inputs):
        # encoder 1 & 2 & 3
        conv10, conv11, conv12, conv13, center1 = self.uencoder1(inputs[:, 5:9, :, :])  # ssn
        conv20, conv21, conv22, conv23, center2 = self.uencoder2(inputs[:, 1:5, :, :])  # mux
        conv30, conv31, conv32, conv33, center3 = self.uencoder3(inputs[:, 9:, :, :])  # vvh
        conv40, conv41, conv42, conv43, center4 = self.uencoder3(inputs[:, :1, :, :])  # footprint


        # decoder 1 & 2 & 3
        com_center = torch.cat([center2, center1, center4], 1)
        final1 = self.udecoder1(conv10, conv11, conv12, conv13, com_center) # ssn class
        final2 = self.udecoder2(conv20, conv21, conv22, conv23, center2) # mux class
        final3 = self.udecoder3(conv30, conv31, conv32, conv33, center3) # vvh class
        final4 = self.final(torch.cat([final1, final2, final3], 1)) # ssn_vvh+mux height

        final1_class = F.softmax(final1,dim=1)
        final2_class = F.softmax(final2,dim=1)
        final4_class = F.softmax(final4,dim=1)
        final3_class = F.softmax(final3,dim=1)
        # deep supervision
        if self.training:
            return final1_class, final2_class, final3_class, final4_class
        else:
            return final4_class, final3_class