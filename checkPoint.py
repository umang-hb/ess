from main import ess_get_working_hours

if __name__ == '__main__':
    daily_remaining_hours, daily_working_hours, week_hours = ess_get_working_hours()
    print('remaining hours: ', daily_remaining_hours, '\nworking hours:', daily_working_hours)
    print('weekly working horus: ', week_hours)
