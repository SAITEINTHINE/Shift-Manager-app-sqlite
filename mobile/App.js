import React, { useEffect, useState } from 'react';
import { View, Text, Button, FlatList, StyleSheet, ActivityIndicator, Alert } from 'react-native';

export default function App() {
    const [shifts, setShifts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://127.0.0.1:5000/api/shifts') // Ensure API is running
            .then(response => response.json())
            .then(data => {
                console.log('Fetched shifts:', data); // Debugging: Log fetched data
                setShifts(data);
            })
            .catch(error => {
                console.error('Error fetching shifts:', error);
                Alert.alert('Error', 'Failed to load shifts.');
            })
            .finally(() => setLoading(false));
    }, []);

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Shift Manager</Text>
            {loading ? (
                <ActivityIndicator size="large" color="#007bff" />
            ) : (
                <FlatList
                    data={shifts}
                    keyExtractor={(item) => item.id.toString()}
                    renderItem={({ item }) => (
                        <View style={styles.shiftItem}>
                            <Text style={styles.shiftText}>📅 Date: {item.date}</Text>
                            <Text style={styles.shiftText}>⏰ Start Time: {item.start_time}</Text>
                            <Text style={styles.shiftText}>⏳ End Time: {item.end_time}</Text>
                            <Text style={styles.shiftText}>☕ Break Start: {item.break_start_time || "N/A"}</Text>
                            <Text style={styles.shiftText}>🍵 Break End: {item.break_end_time || "N/A"}</Text>
                            <Text style={styles.shiftText}>🕒 Break Time (min): {item.break_time || "0"}</Text>
                            <Text style={styles.shiftText}>🌞 Day Wage (¥): ¥{item.hourly_wage_day ? item.hourly_wage_day.toFixed(2) : "0.00"}</Text>
                            <Text style={styles.shiftText}>🌙 Night Wage (¥): ¥{item.hourly_wage_night ? item.hourly_wage_night.toFixed(2) : "0.00"}</Text>
                            <Text style={styles.totalPay}>💰 Total Pay (¥): ¥{item.total_pay ? item.total_pay.toFixed(2) : "0.00"}</Text>
                            <Text style={styles.shiftType}>🔄 Shift Type: {item.shift_type}</Text>
                            <View style={styles.actions}>
                                <Button title="Edit" onPress={() => Alert.alert('Edit Shift', 'Edit feature coming soon!')} />
                                <Button title="Delete" color="red" onPress={() => Alert.alert('Delete Shift', 'Delete feature coming soon!')} />
                            </View>
                        </View>
                    )}
                    ListEmptyComponent={<Text style={styles.emptyText}>No shifts available</Text>} // Show message if no data
                />
            )}
            <Button title="➕ Add Shift" onPress={() => Alert.alert('Add Shift', 'Add Shift feature coming soon!')} />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#f8f9fa',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        textAlign: 'center',
        marginBottom: 20,
        color: '#333',
    },
    shiftItem: {
        padding: 15,
        marginBottom: 10,
        backgroundColor: '#ffffff',
        borderRadius: 8,
        shadowColor: '#000',
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    shiftText: {
        fontSize: 16,
        marginBottom: 5,
        color: '#555',
    },
    totalPay: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#28a745',
        marginTop: 5,
    },
    shiftType: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#007bff',
        marginTop: 5,
    },
    actions: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 10,
    },
    emptyText: {
        textAlign: 'center',
        marginTop: 20,
        fontSize: 18,
        color: '#888',
    },
});
