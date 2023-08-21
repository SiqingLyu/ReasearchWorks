from TifClipper import *


def make_city_dataset(city_img,  testfile_name, city_gt, img_outpath, gt_outpath,test_outpath, block_size = 64):

    dataset = Read_tif(city_img)
    dataset_GT = Read_tif(city_gt)
    dataset_test = Read_tif(testfile_name)

    width = dataset.RasterXSize
    height = dataset.RasterYSize

    xnum = math.floor(width / block_size)
    ynum = math.floor(height / block_size)
    # x_gap, y_gap = 0, 0
    x_gap, y_gap = cal_gaps(dataset_GT, dataset)
    x_gap_test, y_gap_test = cal_gaps(dataset_test, dataset)
    # print(x_gap,y_gap)
    with tqdm(total=int(xnum * ynum)) as pbar:
        for i in range(xnum):
            for j in range(ynum):
                x, y = i * block_size, j * block_size
                try:

                    if(cliptif_4dim(dataset, outpath=img_outpath + "_{0}_{1}.tif".format(i, j), offset_x=x, offset_y=y,
                                    block_xsize=block_size, block_ysize=block_size, Nodata = -3.40282346639e+038)):
                        clipgt_1dim(dataset_GT, outpath=gt_outpath + "_{0}_{1}.tif".format(i, j), offset_x=x + x_gap, offset_y=y + y_gap,
                                block_xsize=block_size, block_ysize=block_size, Nodata=2147483647)
                        cliptif_4dim(dataset_test, outpath=test_outpath + "_{0}_{1}.tif".format(i, j), offset_x=x + x_gap_test, offset_y=y + y_gap_test,
                                     block_xsize=block_size, block_ysize=block_size, Nodata=-3.40282346639e+038)


                except(ValueError):
                    print("ValueError")
                except(IOError):
                    print("IOError")
                pbar.update()
    del dataset
    del dataset_GT
    del dataset_test


def main():
    gt_name = r'D:\Homework\SecondTerm\farm\Ukrine\UKR_small_label\UKR_small_label.tif'

    make_dir(r'D:\Homework\SecondTerm\farm\Dataset256_v2')
    make_dir(r'D:\Homework\SecondTerm\farm\Dataset256_v2\img')
    make_dir(r'D:\Homework\SecondTerm\farm\Dataset256_v2\gt')
    make_dir(r'D:\Homework\SecondTerm\farm\Dataset256_v2\afterwar_test')

    Listfile, allFilename = file_name_tif(r'D:\Homework\SecondTerm\farm\Ukrine\before_war_UTM')
    print(Listfile)
    for i in range(3, len(allFilename)):
        print("processing " + allFilename[i])
        file_name = Listfile[i]
        after_img_id = allFilename[i][-22:]
        after_img_name = 'Ukrine_afterwar' + after_img_id

        testfile_name = r'D:\Homework\SecondTerm\farm\Ukrine_UTM\after_war_UTM' + '\\' + after_img_name + '.tif'
        img_outpath = r'D:\Homework\SecondTerm\farm\Dataset256_v2\img' + '\\' + allFilename[i]
        gt_outpath = r'D:\Homework\SecondTerm\farm\Dataset256_v2\gt' + '\\' + allFilename[i]
        test_outpath = r'D:\Homework\SecondTerm\farm\Dataset256_v2\afterwar_test' + '\\' + allFilename[i]

        print(testfile_name)
        make_city_dataset(file_name, testfile_name, gt_name, img_outpath, gt_outpath, test_outpath, 256)

if __name__ == '__main__':
    main()