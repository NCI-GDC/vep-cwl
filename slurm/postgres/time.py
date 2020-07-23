import postgres.mixins
import postgres.utils

class Time(postgres.mixins.TimeTypeMixin, postgres.utils.Base):

    __tablename__ = 'vep_cwl_metrics'

class TimeWga(postgres.mixins.TimeTypeMixin, postgres.utils.Base):

    __tablename__ = 'vep_wga_cwl_metrics'

class TimeMutectDbsnp(postgres.mixins.TimeTypeMixin, postgres.utils.Base):

    __tablename__ = 'vep_mutect2_dbsnp_rerun_cwl_metrics'