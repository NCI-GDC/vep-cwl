import postgres.mixins
import postgres.utils

class Time(postgres.mixins.TimeTypeMixin, postgres.utils.Base):

    __tablename__ = 'vep_cwl_metrics'
