from test_date import db_data, ordered_list


def match_applications(ordered_list, db_data):
    results = []
    new_id = 1

    for app in ordered_list:
        matched = False
        for entry in db_data:
            search_names = entry['search_names'].split(',')
            if any(app.lower() in name.lower() for name in search_names):
                new_entry = entry.copy()
                new_entry['id'] = new_id
                results.append(new_entry)
                new_id += 1
                matched = True
                break

        if not matched:
            results.append({'id': new_id, 'name': app, 'code': None, 'search_names': None})
            new_id += 1

    return results


if __name__ == '__main__':
    print(match_applications(ordered_list, db_data))