from threading import Lock, Thread, Condition

def doNothing(getName):
    print "~~~"
    print getName
    # print(Thread.get_ident())
    print "~~~"

# def generate_clients(num_of_clients):
#     # Clients placeholder
#     global series_for_multi_clients
#     list_clients = []
#     # Iterate over the clients count
#     for client_id in range(num_of_clients):
#
#         a_client_thread = Thread(target=batch_write_worker)
#         a_client_thread.daemon = True
#
#         # Generate Batch of Metrics for a specific client
#         client_ident = a_client_thread.get_ident()
#         metrics_generator.get_points(batch_size=BATCH_SIZE, measurement_name=measurement_name, client_tag=client_ident)
#         series_for_multi_clients[client_ident] = metrics_generator.series
#
#         # Create a thread and push it to the list
#         list_clients.append(a_client_thread)
#
#     # Return the clients
#     return list_clients

def generate_clients(num_of_clients):
    list_clients = []
    for client_id in range(num_of_clients):
        a_thread = Thread(target=doNothing())
        print "==="
        print(a_thread.getName())
        # print(a_thread.get_ident())
        print "==="
        list_clients.append(a_thread)
    return list_clients


if __name__ == '__main__':
    clients=generate_clients(3)
    # Run the clients! Do batch writes with multi clients
    map(lambda thread: thread.start(), clients)