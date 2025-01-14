import tensorflow as tf
import numpy as np
import argparse
from ops import * 
from my_utils import *
import importlib
from collections import OrderedDict
import os
import sys
from latent_3d_points.src.ae_templates import mlp_architecture_ala_iclr_18, default_train_params
from latent_3d_points.src.autoencoder import Configuration as Conf
from latent_3d_points.src.point_net_ae import PointNetAutoEncoder
from latent_3d_points.src.in_out import snc_category_to_synth_id, create_dir, PointCloudDataSet, \
    load_all_point_clouds_under_folder

import os.path as osp
from latent_3d_points.src.tf_utils import reset_tf_graph

BASE_DIR = os.path.dirname(os.path.abspath(__file__))




def evaluate_all_shapes_scale(batch_indx, setup=None, models=None):
    orig_pts = np.load(os.path.join(setup["dump_dir"], "{}_{}_{}_orig.npy".format(
        setup["victim"], setup["target"], batch_indx)))
    # adv_pts = np.load(os.path.join(out_dir,"{}_{}_{}_adv.npy".format(setup["target"],batch_indx)))
    # the adverserially perturbed data
    nat_pts = np.load(os.path.join(setup["dump_dir"], "{}_{}_{}_adv.npy".format(setup["victim"],setup["target"], batch_indx)))
    # adv_pts = orig_pts + np.random.uniform(high=LIMIT , low=-LIMIT , size=(5,POINT_CLOUD_SIZE,3)) ##########################
    proj_pts = models["ae"].reconstruct(orig_pts)[0]
    # rec_ppts = setup["ae"].reconstruct(adv_pts)[0]
    nat_rec_ppts = models["ae"].reconstruct(nat_pts)[0]
    orig_acc = list(evaluate_ptc(orig_pts,models["PN"],models["PN_PATH"],verbose=False))
    adv_acc = list(evaluate_ptc(nat_pts,models["PN"],models["PN_PATH"],verbose=False))
    proj_acc = list(evaluate_ptc(proj_pts,models["PN"],models["PN_PATH"],verbose=False))
    rec_acc = list(evaluate_ptc(nat_rec_ppts,models["PN"],models["PN_PATH"],verbose=False))

    orig_acc_pp = list(evaluate_ptc(orig_pts,models["PN2"],models["PN2_PATH"],verbose=False))
    adv_acc_pp = list(evaluate_ptc(nat_pts,models["PN2"],models["PN2_PATH"],verbose=False))
    proj_acc_pp = list(evaluate_ptc(proj_pts,models["PN2"],models["PN2_PATH"],verbose=False))
    rec_acc_pp = list(evaluate_ptc(nat_rec_ppts,models["PN2"],models["PN2_PATH"],verbose=False))

    orig_acc_p = list(evaluate_ptc(orig_pts,models["PN1"],models["PN1_PATH"],verbose=False))
    adv_acc_p = list(evaluate_ptc(nat_pts,models["PN1"],models["PN1_PATH"],verbose=False))
    proj_acc_p = list(evaluate_ptc(proj_pts,models["PN1"],models["PN1_PATH"],verbose=False))
    rec_acc_p = list(evaluate_ptc(nat_rec_ppts,models["PN1"],models["PN1_PATH"],verbose=False))

    orig_acc_gcn = list(evaluate_ptc(orig_pts,models["GCN"],models["GCN_PATH"],verbose=False))
    adv_acc_gcn = list(evaluate_ptc(nat_pts,models["GCN"],models["GCN_PATH"],verbose=False))
    proj_acc_gcn = list(evaluate_ptc(proj_pts,models["GCN"],models["GCN_PATH"],verbose=False))
    rec_acc_gcn = list(evaluate_ptc(nat_rec_ppts,models["GCN"],models["GCN_PATH"],verbose=False))
    # b_adv_acc = list(evaluate_ptc(adv_pts,models["PN"],models["PN_PATH"],verbose=False))
    #  b_rec_acc = list(evaluate_ptc(rec_ppts,models["PN"],models["PN_PATH"],verbose=False))
    # b_adv_acc_pp = list(evaluate_ptc(adv_pts,models["PN2"],models["PN2_PATH"],verbose=False))
    #  b_rec_acc_pp = list(evaluate_ptc(rec_ppts,models["PN2"],models["PN2_PATH"],verbose=False))

    orig_acc_r = list(evaluate_ptc(SRS(orig_pts,setup["srs"]),models["test"],models["test_path"],verbose=False))
    adv_acc_r = list(evaluate_ptc(SRS(nat_pts, setup["srs"]), models["test"], models["test_path"], verbose=False))
    # b_adv_acc_r = list(evaluate_ptc(SRS(adv_pts),models["PN"],models["PN_PATH"],verbose=False))
    
    orig_acc_o = list(evaluate_ptc(SOR(orig_pts, setup["sor"]), models["test"], models["test_path"], verbose=False))
    adv_acc_o = list(evaluate_ptc(SOR(nat_pts, setup["sor"]), models["test"], models["test_path"], verbose=False))
    # b_adv_acc_o = list(evaluate_ptc(SOR(adv_pts),models["PN"],models["PN_PATH"],verbose=False))
    
    orig_acc_bust = list(evaluate_ptc(orig_pts, models["test"], models["test_path_robust"], verbose=False))
    adv_acc_bust = list(evaluate_ptc(nat_pts, models["test"], models["test_path_robust"], verbose=False))


    accuracies = {
        "orig_acc": orig_acc,
        "adv_acc": adv_acc,
        "proj_acc": proj_acc,
        "rec_acc": rec_acc,
        "orig_acc_pp": orig_acc_pp,
        "orig_acc_gcn": orig_acc_gcn,
        "orig_acc_p": orig_acc_p,
        "adv_acc_pp": adv_acc_pp,
        "adv_acc_gcn": adv_acc_gcn,
        "adv_acc_p": adv_acc_p,
        "proj_acc_pp": proj_acc_pp,
        "proj_acc_gcn": proj_acc_gcn,
        "proj_acc_p": proj_acc_p,
        "rec_acc_pp": rec_acc_pp,
        "rec_acc_gcn": rec_acc_gcn,
        "rec_acc_p": rec_acc_p,
        "orig_acc_r": orig_acc_r,
        "adv_acc_r": adv_acc_r,
        "orig_acc_o": orig_acc_o,
        "adv_acc_o": adv_acc_o,
        "orig_acc_bust":orig_acc_bust,
        "adv_acc_bust":adv_acc_bust
        }


    # natural_L_2_norm_orig =  np.linalg.norm(orig_pts-proj_pts,axis=(1,2))
    # natural_L_2_norm_adv =  np.linalg.norm(rec_ppts-adv_pts,axis=(1,2))
    # natural_L_2_norm_nat =  np.linalg.norm(nat_rec_ppts-nat_pts,axis=(1,2))
    # natural_L_infty_norm_orig =  np.amax(np.abs(orig_pts-proj_pts),axis=(1,2))
    # natural_L_infty_norm_adv =  np.amax(np.abs(rec_ppts-adv_pts),axis=(1,2))
    # natural_L_infty_norm_nat =  np.amax(np.abs(nat_rec_ppts-nat_pts),axis=(1,2))
    natural_L_cham_norm_orig =   list(1000*chamfer_distance(orig_pts,proj_pts))
    # natural_L_cham_norm_adv =   chamfer_distance(adv_pts,rec_ppts)
    # natural_L_cham_norm_nat =   chamfer_distance(nat_pts,nat_rec_ppts)
    # L_2_norm_adv =  np.linalg.norm(orig_pts-adv_pts,axis=(1,2))
    # L_2_norm_nat =  np.linalg.norm(orig_pts-nat_pts,axis=(1,2))
    # L_infty_norm_adv =    np.amax(np.abs(orig_pts-adv_pts),axis=(1,2))
    # L_infty_norm_nat =   np.amax(np.abs(orig_pts-nat_pts),axis=(1,2))
    # L_cham_norm_adv =   chamfer_distance(orig_pts,adv_pts)
    # L_cham_norm_nat =   chamfer_distance(orig_pts,nat_pts)
    # L_emd_norm_adv =   emd_distance(orig_pts,adv_pts)
    # L_emd_norm_nat =   emd_distance(orig_pts,nat_pts)

    norms = {
        # "natural_L_2_norm_orig": natural_L_2_norm_orig,
        # "natural_L_2_norm_adv": natural_L_2_norm_adv,
        # "natural_L_2_norm_nat": natural_L_2_norm_nat,
        # "natural_L_infty_norm_orig": natural_L_infty_norm_orig,
        # "natural_L_infty_norm_adv": natural_L_infty_norm_adv,
        # "natural_L_infty_norm_nat": natural_L_infty_norm_nat,
        # "L_2_norm_adv": L_2_norm_adv,
        # "L_2_norm_nat": L_2_norm_nat,
        # "L_infty_norm_adv": L_infty_norm_adv,
        # "L_infty_norm_nat": L_infty_norm_nat,
        # "L_cham_norm_adv": L_cham_norm_adv,
        # "L_cham_norm_nat": L_cham_norm_nat,
        # "L_emd_norm_adv": L_emd_norm_adv,
        # "L_emd_norm_nat": L_emd_norm_nat,
        "natural_L_cham_norm_orig": natural_L_cham_norm_orig
        # "natural_L_cham_norm_adv": natural_L_cham_norm_adv,
        # "natural_L_cham_norm_nat": natural_L_cham_norm_nat
    }

    return accuracies, norms


def evaluate(setup, results,models,targets_list, victims_list):

    top_out_dir = osp.join(BASE_DIR, "latent_3d_points", "data")
    # print(BASE_DIR)


# Top-dir of where point-clouds are stored.
    top_in_dir = osp.join(BASE_DIR, "latent_3d_points", "data",
                        "shape_net_core_uniform_samples_2048")


    # experiment_name = 'single_class_ae'
    experiment_name = 'new_ae'

    n_pc_ppoints = 1024  # 2048                # Number of points per model.
    bneck_size = 128                  # Bottleneck-AE size
    # Loss to optimize: 'emd' or 'chamfer'             # Bottleneck-AE size
    ae_loss = 'chamfer'
    train_params = default_train_params()
    encoder, decoder, enc_args, dec_args = mlp_architecture_ala_iclr_18(
        n_pc_ppoints, bneck_size)
    train_dir = create_dir(osp.join(top_out_dir, experiment_name))


    conf = Conf(n_input=[n_pc_ppoints, 3],
                loss=ae_loss,
                training_epochs=train_params['training_epochs'],
                batch_size=train_params['batch_size'],
                denoising=train_params['denoising'],
                learning_rate=train_params['learning_rate'],
                train_dir=train_dir,
                loss_display_step=train_params['loss_display_step'],
                saver_step=train_params['saver_step'],
                z_rotate=train_params['z_rotate'],
                encoder=encoder,
                decoder=decoder,
                encoder_args=enc_args,
                decoder_args=dec_args
                )
    conf.experiment_name = experiment_name
    conf.held_out_step = 5   # How often to evaluate/print out loss on
    # held_out data (if they are provided in ae.train() ).
    conf.save(osp.join(train_dir, 'configuration'))

    load_pre_trained_ae = True
    restore_epoch = 500
    if load_pre_trained_ae:
        conf = Conf.load(train_dir + '/configuration')
        reset_tf_graph()
        ae = PointNetAutoEncoder(conf.experiment_name, conf)
        ae.restore_model(conf.train_dir, epoch=restore_epoch, verbose=True)
        models["ae"] = ae

    # all_resulting_corrects = []
    # natural_L_2_norm_orig = []
    # natural_L_2_norm_adv = []
    # natural_L_2_norm_nat = []
    # natural_L_infty_norm_orig = []
    # natural_L_infty_norm_adv = []
    # natural_L_infty_norm_nat = []
    # L_2_norm_adv = []
    # L_2_norm_nat = []
    # L_infty_norm_adv = []
    # L_infty_norm_nat = []
    # L_cham_norm_adv = []
    # L_cham_norm_nat = []
    # L_emd_norm_adv = []
    # L_emd_norm_nat = []
    # natural_L_cham_norm_orig = []
    # natural_L_cham_norm_adv = []
    # natural_L_cham_norm_nat = []
    accuracies_disc = {
        "orig_acc": "original accuracy on PointNet ",
        "adv_suc": "natural adverserial sucess rate on PointNet ",
        "adv_acc": "natural adverserial accuracy on PointNet ",
        "proj_acc": "projected accuracy on PointNet ",
        "rec_suc": "defended natural adverserial sucess rate on PointNet ",
        "rec_acc": "reconstructed defense accuracy on PointNet ",
        "orig_acc_pp": "original accuracy on PointNet_++ ",
        "orig_acc_gcn": "original accuracy on DGCN",
        "orig_acc_p": "original accuracy on PointNet_+ ",
        "adv_suc_pp": "natural adverserial sucess rate on PointNet_++ ",
        "adv_suc_gcn": "natural adverserial sucess rate on DGCN",
        "adv_suc_p": "natural adverserial sucess rate on PointNet_+ ",
        "adv_acc_pp": "natural adverserial accuracy on PointNet_++ ",
        "adv_acc_gcn": "natural adverserial accuracy on DGCN",
        "adv_acc_p": "natural adverserial accuracy on PointNet_+ ",
        "proj_acc_pp": "projected accuracy on PointNet_++ ",
        "proj_acc_gcn": "projected accuracy on DGCN",
        "proj_acc_p": "projected accuracy on PointNet_+ ",
        "rec_suc_pp": "defended natural adverserial sucess rate on PointNet_++ ",
        "rec_suc_gcn": "defended natural adverserial sucess rate on DGCN",
        "rec_suc_p": "defended natural adverserial sucess rate on PointNet_+ ",
        "rec_acc_pp": "reconstructed defense accuracy on PointNet_++ ",
        "rec_acc_gcn": "reconstructed defense accuracy on DGCN",
        "rec_acc_p": "reconstructed defense accuracy on PointNet_+ ",
        "b_adv_suc": "baseline adverserial sucess rate on PointNet ",
        "b_adv_acc": "baseline adverserial accuracy on PointNet ",
        "b_rec_suc": "baseline defended natural adverserial sucess rate on PointNet ",
        "b_rec_acc": "baselin ereconstructed defense accuracy on PointNet ",
        "b_adv_suc_pp": "baseline adverserial sucess rate on PointNet_++ ",
        "b_adv_suc_gcn": "baseline adverserial sucess rate on DGCN",
        "b_adv_suc_p": "baseline adverserial sucess rate on PointNet_+ ",
        "b_adv_acc_pp": "baseline adverserial accuracy on PointNet_++ ",
        "b_adv_acc_gcn": "baseline adverserial accuracy on DGCN",
        "b_adv_acc_p": "baseline adverserial accuracy on PointNet_+ ",
        "b_rec_suc_pp": "baseline defended natural adverserial sucess rate on PointNet_++ ",
        "b_rec_suc_gcn": "baseline defended natural adverserial sucess rate on DGCN",
        "b_rec_suc_p": "baseline defended natural adverserial sucess rate on PointNet_+ ",
        "b_rec_acc_pp": "baselin ereconstructed defense accuracy on PointNet_++ ",
        "b_rec_acc_gcn": "baselin ereconstructed defense accuracy on DGCN",
        "b_rec_acc_p": "baselin ereconstructed defense accuracy on PointNet_+ ",
        "orig_acc_r": "original accuracy under Random defense",
        "adv_suc_r": "natural adverserial accuracy under Random defense",
        "adv_acc_r": "natural adverserial sucess rate under Random defense",
        "b_adv_suc_r": "baseline  adverserial accuracy under Random defense",
        "b_adv_acc_r": "baseline  adverserial sucess rate under Random defense",
        "orig_acc_o": "original accuracy under Outlier defense",
        "adv_suc_o": "natural adverserial accuracy under Outlier defense",
        "adv_acc_o": "natural adverserial sucess rate under Outlier defense",
        "b_adv_suc_o": "baseline  adverserial accuracy under Outlier defense",
        "b_adv_acc_o": "baseline  adverserial sucess rate under Outlier defense",
        "orig_acc_bust": "original accuracy under Robust model",
        "adv_acc_bust": "natural adverserial accuracy under Robust model"
        }

    # accuracies_names  = [
    #     "orig_acc", "adv_acc", "proj_acc", "rec_acc", "orig_acc_pp", , "orig_acc_p"
    #     "adv_acc_pp", "proj_acc_pp", "rec_acc_pp", "adv_acc_p", "proj_acc_p", "rec_acc_p""orig_acc_r",
    #     "adv_acc_r","orig_acc_o","adv_acc_o"]
    norms_names = ["natural_L_cham_norm_orig"]
    ev_results = ListDict(accuracies_disc.keys()+norms_names)
    # norms_results = ListDict(norms_names)
    setups = ListDict(setup.keys())
    save_results(setup["results_file"], ev_results+ setups)
    for target in targets_list:
        setup["target"] = target
        for victim in victims_list:
            if victim == setup["target"]:
                continue
            setup["victim"] = victim
            for batch_indx in range(int(setup["batch_size"])):
                predictions, norms = evaluate_all_shapes_scale(batch_indx=batch_indx, setup=setup,models=models)
                [setups.append(setup) for ii in range(setup["batch_size"])]
                # norms_results.remove(norms_results - ListDict(norms))
                # norms_results.partial_extend(ListDict(norms))
                ev_results.remove(ev_results - ListDict(predictions) - ListDict(norms))
                ev_results.partial_extend(
                    ListDict(predictions)).partial_extend(ListDict(norms))
                save_results(setup["results_file"], ev_results+setups)

    save_results(setup["results_file"], ev_results +setups+results)
    return ev_results 
