//
//  SocketSignal.swift
//  M1_kawanaka
//
//  Created by kawanaka masaki on 2021/10/06.
//

import Foundation
import SocketIO

protocol SocketProtcol {
    func aaa()
}

class SocketSignal {
    var ipAddress: String!
    var manager: SocketManager!
    var socket: SocketIOClient!
    var delegate: SocketProtcol!
    
    func connect() {
        manager = SocketManager(socketURL: URL(string: "http://" + ipAddress)!, config: [.log(true), .compress])
        socket = manager.defaultSocket
        socket.connect()
        self.delegate.aaa()
    }
    
    func disConnect(){
            socket.disconnect()
    }
}


