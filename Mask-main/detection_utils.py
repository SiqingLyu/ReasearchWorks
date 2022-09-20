from tqdm import tqdm
from dataloaders.dataloaders import *
from torch.nn.functional import l1_loss, mse_loss 
from pytorch_tools import *
from torchvision.ops import boxes as box_ops
import copy
from functools import reduce

class detection_base(pl_model_base):
    def init_end(self):
        self.iou_threshold = 0.5
        if not hasattr(self, 'loss_weight'):
            self.loss_weight = {}
        if not hasattr(self, 'gt_rpn_training'):
            self.gt_rpn_training = False
        self.positive_fraction_bak = self.main_model.roi_heads.fg_bg_sampler.positive_fraction
        self.reset_metric_collection()

    def reset_metric_collection(self):
        self.nos_collection = result_collection('nos')
        self.area_collection = result_collection('area')
        self.score_collection = result_collection('scores')
        self.iou_collection = result_collection('iou')
        self.file_names = []
        self.seg_metirx = [[] for i in range(5)]

        self.nos_collection_gt = result_collection('nos')
        self.score_collection_gt = result_collection('scores')
        self.seg_metirx_gt = [[] for i in range(5)]
        
    def configure_optimizers(self):
        optimizer = optim.SGD(
            self.parameters(),
            lr=self.hparams['lr'],
            momentum=0.9
        )
        lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
                                                       step_size=3,
                                                       gamma=0.1)
        # lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
        #                                                step_size=3,
        #                                                gamma=0.1)
        #optimizer = optim.Adam(self.parameters(), lr=self.hparams.lr)
        #scheduler = lr_scheduler.CosineAnnealingLR(optimizer, T_max=10)
        #scheduler = lr_scheduler.ExponentialLR(optimizer, gamma=0.1)
        '''
        lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
                                                   step_size=3,
                                                   gamma=0.1)'''
        return [optimizer], [lr_scheduler]
    
    def get_dataset(self):
        if self.hparams['label_is_nos'] is True:
            print('【label 为层数！】')
        else:
            print('【label 为1/0！】')
        data_path = self.hparams['data_path']
        trainimg, trainlab, valimg, vallab, _, _ = make_dataset(data_path, split=[0.8,0.1,0.1])
        train_dataset = MaskRcnnDataloader(trainimg, trainlab, augmentations=True, area_thd=1,  label_is_nos=self.hparams['label_is_nos'])
        val_dataset = MaskRcnnDataloader(valimg, vallab, augmentations=False, area_thd=1,  label_is_nos=self.hparams['label_is_nos'])
        return train_dataset,val_dataset

    def forward(self,x):
        return self.main_model(*x)

    def set_gt_rpn(self, book):
        if book:
            self.main_model.rpn.gt_rpn = True
            self.main_model.roi_heads.gt_rpn = True
            self.main_model.roi_heads.fg_bg_sampler.positive_fraction = 1.0
        else:
            self.main_model.rpn.gt_rpn = False
            self.main_model.roi_heads.gt_rpn = False
            self.main_model.roi_heads.fg_bg_sampler.positive_fraction = self.positive_fraction_bak

    def on_epoch_start(self):
        self.set_gt_rpn(self.gt_rpn_training)

    '''
    pytorch-lightning 下的trainloop伪代码，
    根据伪代码中函数出现顺序判断需要重写的函数
    def train_loop():
        on_train_epoch_start()
        train_outs = []
        for train_batch in train_dataloader():
            on_train_batch_start()

            # ----- train_step methods -------
            out = training_step(batch)
            train_outs.append(out)

            loss = out.loss

            backward()
            on_after_backward()
            optimizer_step()
            on_before_zero_grad()
            optimizer_zero_grad()

            on_train_batch_end(out)

            if should_check_val:
                val_loop()

        # end training epoch
        logs = training_epoch_end(outs)
    '''

    def training_step(self, batch, batch_idx):
        loss_dict = self(batch)
        loss = reduce(add, loss_dict.values())
        return {
            'loss': loss,
            'progress_bar': loss_dict,
            'log': loss_dict
        }

    # def optimizer_step(self, epoch, batch_idx, optimizer, optimizer_idx,
    #                    optimizer_closure, on_tpu=False, using_native_amp=False, using_lbfgs=False):
    #     print('=================')
    #     # self.configure_gradient_clipping(self.trainer.optimizers, optimizer_idx, 4, "norm")
    #     # torch.nn.utils.clip_grad_norm_(self.parameters(), 3, norm_type=2)
    #     optimizer.step(closure=optimizer_closure)

    # def configure_gradient_clipping(self, optimizer, optimizer_idx, gradient_clip_val, gradient_clip_algorithm):
    #     self.clip_gradients(
    #         optimizer = self.trainer.optimizers,
    #         gradient_clip_val=gradient_clip_val,
    #         gradient_clip_algorithm=gradient_clip_algorithm
    #     )
    # implement your own custom logic to clip gradients for generator (optimizer_idx=0)

    # def on_before_optimizer_step(self, optimizer, optimizer_idx):
    #     # example to inspect gradient information in tensorboard
    #     torch.nn.utils.clip_grad_norm_(self.parameters(), 3, norm_type=2)
    #     print("++++++")

    '''
    validationloop 的伪代码
    def val_loop():
    model.eval()
    torch.set_grad_enabled(False)

    on_validation_epoch_start()
    val_outs = []
    for val_batch in val_dataloader():
        on_validation_batch_start()

        # -------- val step methods -------
        out = validation_step(val_batch)
        val_outs.append(out)

        on_validation_batch_end(out)

    validation_epoch_end(val_outs)
    on_validation_epoch_end()

    # set up for train
    model.train()
    torch.set_grad_enabled(True)
    '''

    def postprocess_output(self, output, gts):
        return output, copy.deepcopy(gts)

    def validation_step(self, batch, batch_idx):
        images, gts = batch
        #if not self.gt_rpn_training:
        self.set_gt_rpn(False)
        show_inxes = [np.random.randint(len(images))]
        output = self([images, copy.deepcopy(gts)])
        output, gts_post = self.postprocess_output(output, gts)
        for inx, (img, target, predict) in enumerate(zip(images,gts_post,output)):
            predict = detach_all(predict)
            t_boxes = target['boxes']
            target['labels'] = target['labels'].float()
            p_boxes = predict['boxes']
            p_score = predict['scores']
            if len(p_boxes) == 0:
                TP_pre_inx, TP_gt_inx, FP_p_inx = [[]] * 3
                FN_t_inx = list(range(len(t_boxes)))
                iou_pre = p_score
            else:
                match_quality_matrix = box_ops.box_iou(t_boxes, p_boxes)
                TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx, iou_pre = get_match_inx(match_quality_matrix, self.iou_threshold)
            predict['iou'] = iou_pre
            TP_p, TP_t, FP_p, FN_t = self.nos_collection.collect(target, predict, TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx)
            _ = self.area_collection.collect(target, None, TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx)
            _ = self.score_collection.collect(None, predict, TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx)
            _ = self.iou_collection.collect(None, predict, TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx)
            self.file_names.append(target["file_name"])

            if 'masks' in predict.keys():
                mask_true = target['masks'].any(0).bool()
                mask_pred = (predict['masks'] > 0.5).any(0)[0]
                inter = (mask_true & mask_pred).sum()
                union = (mask_true | mask_pred).sum()
                TPTN = (mask_true == mask_pred).sum()
                pos, gt = mask_pred.sum(), mask_true.sum()
                self.seg_metirx[0].append(inter)
                self.seg_metirx[1].append(union)
                self.seg_metirx[2].append(TPTN)
                self.seg_metirx[3].append(pos)
                self.seg_metirx[4].append(gt)
            if inx in show_inxes:
                self.sample_step_end(locals())
            
        self.set_gt_rpn(True)
        output = self([images, copy.deepcopy(gts)])
        output, gts_post = self.postprocess_output(output, gts_post)
        for inx, (img, target, predict) in enumerate(zip(images,gts_post,output)):
            predict = detach_all(predict)
            t_boxes = target['boxes']
            target['labels'] = target['labels'].float()
            p_boxes = predict['boxes']
            p_score = predict['scores']
            if len(p_boxes) == 0:
                TP_pre_inx, TP_gt_inx, FP_p_inx = [[]] * 3
                FN_t_inx = list(range(len(t_boxes)))
            else:
                match_quality_matrix = box_ops.box_iou(t_boxes, p_boxes)
                TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx, iou_pre = get_match_inx(match_quality_matrix, 1)

            TP_p, TP_t, FP_p, FN_t = self.nos_collection_gt.collect(target, predict, TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx)
            #_ = self.area_collection.collect(target, None, TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx)
            _ = self.score_collection_gt.collect(None, predict, TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx)
            #self.file_names.append(target["file_name"])

            if 'masks' in predict.keys():
                mask_true = target['masks'].any(0).bool()
                mask_pred = (predict['masks'] > 0.5).any(0)[0]
                inter = (mask_true & mask_pred).sum()
                union = (mask_true | mask_pred).sum()
                TPTN = (mask_true == mask_pred).sum()
                pos, gt = mask_pred.sum(), mask_true.sum()
                self.seg_metirx_gt[0].append(inter)
                self.seg_metirx_gt[1].append(union)
                self.seg_metirx_gt[2].append(TPTN)
                self.seg_metirx_gt[3].append(pos)
                self.seg_metirx_gt[4].append(gt)
            if inx in show_inxes:
                self.sample_step_end(locals())

        return {}

    def get_val_result(self,output):
        log_dict = {}
        #if not self.gt_rpn_training:
        TP_p, TP_t, FP_p, FN_t = self.nos_collection.cat_all()
        P, R, F1 = PRF1(TP_p, TP_t, FP_p, FN_t)
        if self.hparams['nos_task']:
            MAE, RMSE, res_rel, IoU_NoS = NoS_metric(TP_p, TP_t, FP_p, FN_t)
            log_dict = make_log('', locals(), MAE, F1, P, R, RMSE, res_rel, IoU_NoS)
            val_loss = MAE
        else:
            log_dict = make_log('', locals(), F1, P, R)
            val_loss = F1
        if self.seg_metirx[0]:
            I, U, TPTN, POS, GT = torch.tensor(self.seg_metirx).sum(1).float()
            seg_IoU = I / U
            seg_acc = TPTN / (len(self.seg_metirx[2])* 128**2)
            seg_P = I / POS
            seg_R = I / GT
            seg_log = make_log('', locals(), seg_acc, seg_IoU, seg_P, seg_R)
            log_dict.update(seg_log)
        
        TP_p, TP_t, FP_p, FN_t = self.nos_collection_gt.cat_all()
        P_all, R_all, F1_all = PRF1(TP_p, TP_t, FP_p, FN_t)
        if self.hparams['nos_task']:
            MAE_all, RMSE_all, res_rel_all, IoU_NoS_all = NoS_metric(TP_p, TP_t, FP_p, FN_t)
            log_dict_all = make_log('', locals(), MAE_all, F1_all, P_all, R_all, RMSE_all, res_rel_all, IoU_NoS_all)
            val_loss = MAE_all
        else:
            log_dict_all = make_log('', locals(), F1_all, P_all, R_all)
            #val_loss = F1
        if self.seg_metirx_gt[0]:
            I, U, TPTN, POS, GT = torch.tensor(self.seg_metirx_gt).sum(1).float()
            seg_IoU_all = I / U
            seg_acc_all = TPTN / (len(self.seg_metirx_gt[2])* 128**2)
            seg_P_all = I / POS
            seg_R_all = I / GT
            seg_log_all = make_log('', locals(), seg_acc_all, seg_IoU_all, seg_P_all, seg_R_all)
            log_dict_all.update(seg_log_all)

        log_dict.update(log_dict_all)
        return {
            'val_loss': val_loss,
            'log': log_dict
        }
    
    def validation_epoch_end(self,output):
        out = self.get_val_result(output)
        self.reset_metric_collection()
        return out
    
    def test_step(self, batch, batch_idx):
        return self.validation_step(batch, batch_idx)
    
    def test_epoch_end(self, output):
        re_dict = self.get_val_result(output)
        self.result = re_dict['log']
        nos_p, nos_t, _, _ = self.nos_collection.cat_all(True)
        iou = self.iou_collection.cat_all(True)[0]
        score = self.score_collection.cat_all(True)[0]
        area = self.area_collection.cat_all(True)[1]

        tp_dict = dict(
            nos_gt = nos_t,
            nos_pre = nos_p,
            iou = iou,
            score = score,
            area = area
        )
        pd.DataFrame(tp_dict).to_csv(self.exp_folder/'TP_data.csv')

        nos_p, nos_t, _, _ = self.nos_collection_gt.cat_all(True)
        score = self.score_collection_gt.cat_all(True)[0]
        pd.DataFrame(dict(
            nos_gt = nos_t,
            nos_pre = nos_p,
            score = score
            )
        ).to_csv(self.exp_folder/'all_data.csv')
        self.reset_metric_collection()
        return re_dict


def get_match_inx(match_quality_matrix, iou_threshold = 0.5):
    # match_quality_matrix.shape:(len(t_boxes), len(p_boxes))
    num_t, num_p = match_quality_matrix.shape
    gt2pre_inx = torch.full((num_t,), -1, dtype = torch.long)
    pre2gt_inx = torch.full((num_p,), -1, dtype = torch.long)
    iou_pre = torch.full((num_p,), -1.0)
    col_numel = match_quality_matrix.shape[1]
    while True:
        # 找出最IoU值最大的一对pre与gt, 获得最大值及其所在的行列号
        max_inx = match_quality_matrix.argmax()
        row = max_inx // col_numel
        col = max_inx % col_numel
        max_value = match_quality_matrix[row, col].item()
        # 若当前最大的IoU小于给定阈值，则结束匹配
        if max_value < iou_threshold:
            break
        # 为匹配到的gt/pre记录其对应的pre/gt的索引
        gt2pre_inx[row] = col
        pre2gt_inx[col] = row
        # 设置标记，该组配对将不再被匹配到
        match_quality_matrix[row] = -1
        match_quality_matrix[:, col] = -1
        #记录匹配到的prediction的iou，未匹配到的值为-1
        iou_pre[col] = max_value
    #转化为inx索引
    TP_pre_inx = gt2pre_inx[gt2pre_inx != -1]
    TP_gt_inx = torch.tensor([i for i,v in enumerate(gt2pre_inx) if v != -1]).long()
    FP_pre_inx = torch.where(pre2gt_inx == -1)[0]
    FN_gt_inx = torch.where(gt2pre_inx == -1)[0]
    return TP_pre_inx, TP_gt_inx, FP_pre_inx, FN_gt_inx, iou_pre

class result_collection(object):
    def __init__(self, key):
        self.key = key
        self.reset()
    def collect(self, target, pre, TP_pre_inx, TP_gt_inx, FP_p_inx, FN_t_inx):
        TP_p, TP_t, FP_p, FN_t = [torch.tensor([]) for i in range(4)]
        if target is not None:
            t_labels = target[self.key]
            TP_t, FN_t = t_labels[TP_gt_inx], t_labels[FN_t_inx]
        self.TP_t_label_all.append(TP_t)
        self.FN_t_label_all.append(FN_t)
        if pre is not None:
            p_labels = pre[self.key]
            TP_p, FP_p = p_labels[TP_pre_inx], p_labels[FP_p_inx]
        self.TP_p_label_all.append(TP_p)
        self.FP_p_label_all.append(FP_p)
        return  TP_p, TP_t, FP_p, FN_t

    def reset(self):
        self.TP_t_label_all = []
        self.TP_p_label_all = []
        self.FP_p_label_all = []
        self.FN_t_label_all = []
        
    def cat_all(self, return_numpy=False):
        ret = list(map(torch.cat,[self.TP_p_label_all, self.TP_t_label_all, self.FP_p_label_all, self.FN_t_label_all]))
        return to_numpy(ret) if return_numpy else ret

def NoS_metric(TP_p, TP_t, FP_p=None, FN_t=None):
    '''return MAE, RMSE, res_rel, IoU_NoS'''
    has_nos = TP_t != 0
    valid_gt, valid_pre = TP_t[has_nos], TP_p[has_nos]
    if len(valid_gt) == 0:
        MAE, RMSE, res_rel, IoU_NoS = torch.tensor([9999]*4)
        return MAE, RMSE, res_rel, IoU_NoS
    if isinstance(valid_gt, np.ndarray):
        valid_gt, valid_pre = torch.from_numpy(valid_gt), torch.from_numpy(valid_pre)
    
    MAE = l1_loss(valid_pre, valid_gt)
    RMSE = mse_loss(valid_pre, valid_gt)**0.5

    res_rel = torch.abs(valid_gt - valid_pre) / valid_gt
    res_rel = res_rel.mean()
    nos_stack = torch.stack([valid_gt.type_as(valid_pre), valid_pre])
    nos_min, _ = nos_stack.min(0)
    nos_max, _ = nos_stack.max(0)
    IoU_NoS = nos_min / nos_max
    IoU_NoS = IoU_NoS.mean()
    return MAE, RMSE, res_rel, IoU_NoS

def PRF1(TP_p, TP_t, FP_p, FN_t):
    assert len(TP_p) == len(TP_t)
    P = len(TP_p)/(len(TP_p) + len(FP_p) + 0.00001)
    R = len(TP_p)/(len(TP_p) + len(FN_t) + 0.00001)
    F1 = (2 * P * R)/(P + R) if P + R != 0 else 0
    P, R, F1 = torch.tensor([P, R, F1])
    return P, R, F1
