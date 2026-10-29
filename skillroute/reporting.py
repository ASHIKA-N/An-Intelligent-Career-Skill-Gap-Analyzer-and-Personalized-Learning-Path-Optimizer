"""Safe, usable CSV exports."""
import pandas as pd


def export_gaps(rows):
    return pd.DataFrame(rows).to_csv(index=False).encode('utf-8')


def export_attempts(attempts):
    return pd.DataFrame(attempts,columns=['created','skill','score','version','before_state','after_state']).to_csv(index=False).encode('utf-8')
