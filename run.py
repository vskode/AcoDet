from AcoDet.annotate import run_annotation, filter_annots_by_thresh
from AcoDet.train import run_training, save_model
from AcoDet.tfrec import write_tfrec_dataset
from AcoDet.hourly_presence import compute_hourly_pres, calc_val_diff
from AcoDet.evaluate import create_overview_plot
from AcoDet.combine_annotations import generate_final_annotations
from AcoDet.models import init_model
from AcoDet.create_session_file import create_session_file
create_session_file()
import AcoDet.global_config as conf

def main():
    if conf.RUN_CONFIG == 1:
        if conf.PRESET == 1:
            run_annotation()
        elif conf.PRESET == 2:
            filter_annots_by_thresh()
        elif conf.PRESET == 3:
            compute_hourly_pres(sc=True)
        elif conf.PRESET == 4:
            compute_hourly_pres()
        elif conf.PRESET == 5:
            pass # TODO hourly preds mit varying limits
        elif conf.PRESET == 6:
            calc_val_diff()
        elif conf.PRESET == 0:
            time_start = run_annotation()
            filter_annots_by_thresh(time_start)
            compute_hourly_pres(time_start, sc=True)
        
    elif conf.RUN_CONFIG == 2:
        if conf.PRESET == 1:
            generate_final_annotations()
            write_tfrec_dataset()
        elif conf.PRESET == 2:
            generate_final_annotations(active_learning=False)
            write_tfrec_dataset(active_learning=False)
            
    elif conf.RUN_CONFIG == 3:
        if conf.PRESET == 1:
            run_training()
        elif conf.PRESET == 2:
            create_overview_plot()
        elif conf.PRESET == 3:
            create_overview_plot('2022-05-00_00')
        elif conf.PRESET == 4:
            save_model('FlatHBNA', init_model())
            
if __name__ == '__main__':
    main()