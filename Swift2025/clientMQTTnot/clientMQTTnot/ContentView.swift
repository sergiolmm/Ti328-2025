//
//  ContentView.swift
//  clientMQTTnot
//
//  Created by Sérgio Luiz Moral Marques on 10/09/25.
//

import SwiftUI
import CocoaMQTT

struct MyData: Codable {
    let temp: Int
}

// classe de gerencia do MQTT
class MQTTManager: NSObject, ObservableObject, CocoaMQTTDelegate{
    
    @Published var isConnected: Bool = false
    @Published var isSubriscribed: Bool =   false
    @Published var messages: [String] = []
    @Published var messagesOut: [String] = []
    @Published var receiveMessage : String = ""
    private var mqtt: CocoaMQTT?
    
    func mqtt(_ mqtt: CocoaMQTT, didConnectAck ack: CocoaMQTTConnAck) {
        if ack == CocoaMQTTConnAck.accept {
            DispatchQueue.main.async { self.isConnected = true }
            print("Conectou ao Broker")
        }
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didPublishMessage message: CocoaMQTTMessage, id: UInt16) {
        DispatchQueue.main.async {
            self.receiveMessage = message.string ?? ""
            self.messagesOut.append("\(message.topic): \(self.receiveMessage)")
        }
        print("Mensagem publicadas: \(message.string ?? "nil")")
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didPublishAck id: UInt16) {
        print("didPublishAck -> \(id)")
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didReceiveMessage message: CocoaMQTTMessage, id: UInt16) {
        let text = message.string ?? ""
        print("Msg recebidas : \(text)")
        do {
            let decodedData = try JSONDecoder().decode(MyData.self, from: text.data(using: .utf8)!)
            print("Name: \(decodedData.temp)")
        } catch {
            print("Error decoding JSON: \(error)")
        }
        DispatchQueue.main.async{
            self.messages.append("\(message.topic): \(text)")
        }
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didSubscribeTopics success: NSDictionary, failed: [String]) {
        DispatchQueue.main.async{
            self.isSubriscribed = true
        }
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didUnsubscribeTopics topics: [String]) {
        DispatchQueue.main.async{
            self.isSubriscribed = false
        }
    }
    
    func mqttDidPing(_ mqtt: CocoaMQTT) {
        print("PING")
    }
    
    func mqttDidReceivePong(_ mqtt: CocoaMQTT) {
        print("pong")
    }
    
    func mqttDidDisconnect(_ mqtt: CocoaMQTT, withError err: (any Error)?) {
        print("Desconectei do Broker - \(err?.localizedDescription ?? "")")
        DispatchQueue.main.async{
            self.isSubriscribed = false
            self.isConnected = false
            self.messages.removeAll()
            self.messagesOut.removeAll()
        }
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didReceive trust: SecTrust, completionHandler: @escaping (Bool) -> Void){
        var error: CFError?
        let isServerTrusted = SecTrustEvaluateWithError(trust, &error)
        if isServerTrusted {
            print("Certificado valido")
            completionHandler(true)
        } else {
            print("Falha no certificado \(String(describing: error))")
            
        }
    }
    
    // variaveis de apoio para a conexão MQTT
    var host: String = "73a3246b4410491692df6b23c34b84cc.s1.eu.hivemq.cloud"
    var port: UInt16 = 8883
    var username: String? = "noturno"
    var password: String? = "Cotuca25"
    var topic: String = "media"
    
    // construtor e metodos da classe MQTTManager
    
    override init() {
        super.init()
    }
    
    func connect() {
        let clientID = "SwiftUIClient" + String(ProcessInfo().processIdentifier)
        
        mqtt = CocoaMQTT(clientID: clientID, host: host, port: port)
        mqtt?.username = username
        mqtt?.password = password
        mqtt?.enableSSL = true
        mqtt?.allowUntrustCACertificate = true
        mqtt?.sslSettings = [
            kCFStreamSSLPeerName as String : host as NSObject
        ]
        mqtt?.logLevel = .debug
        mqtt?.autoReconnect  = true
        mqtt?.keepAlive = 60
        mqtt?.delegate = self
        mqtt?.connect()
    }
    
    func disconnect() {
        mqtt?.disconnect()
    }
    
    func subscribe(to topic: String? = nil){
        guard let mqtt else {return}
        mqtt.subscribe(topic ?? self.topic, qos: .qos0)
    }
    
    func unsubscribe(to topic: String? = nil){
        guard let mqtt else {return}
        mqtt.unsubscribe(topic ?? self.topic)
    }
    
    func publish(_ text: String, to topic: String? = nil){
        guard let mqtt else { return }
        mqtt.publish(topic ?? self.topic, withString: text, qos: .qos0)
    }
 
}





struct ContentView: View {
    @StateObject private var manager = MQTTManager()
    @State private var input = "{\"temp\": 10}"
    @State private var customTopic = "media"
    @State private var isRedOn = false
    @State private var isGreenOn = false
    @State private var isYellowOn = false
    var body: some View {
        NavigationView{
            VStack(spacing: 16) {
                HStack {
                    Circle()
                        .fill(manager.isConnected ? .green : .red)
                        .frame(width: 10, height: 10)
                    Text(manager.isConnected ? "Conectado (MQTT + SSL": "Desconectado")
                        .font(.headline)
                    Spacer()
                }
                HStack{
                    Button(manager.isConnected ? "Desconectar" : "Conectar") {
                        manager.isConnected ? manager.disconnect() : manager.connect()
                    }
                    .buttonStyle(.borderedProminent)
                    Button(manager.isSubriscribed ? "Desassinar" : "Assinar"){
                        manager.isSubriscribed ? manager.unsubscribe() :
                        manager.subscribe()
                    }.disabled(!manager.isConnected)
                        .buttonStyle(.borderedProminent)
                }
                HStack{
                    TextField("Tópico", text: $customTopic)
                        .textFieldStyle(.roundedBorder)
                        .frame(minWidth: 100)
                    TextField("Mensagem", text: $input)
                        .textFieldStyle(.roundedBorder)
                    Button("Enviar"){
                        guard !input.isEmpty else {return}
                        
                        manager.publish(input, to: customTopic)
                    }.disabled(!manager.isConnected)
                }
                HStack{
                    Spacer()
                  Button("Red"){
                      var msg = "{\"red\": 1}"
                      if isRedOn {
                          msg = "{\"red\": 0}"
                          isRedOn = false
                      } else {
                          msg = "{\"red\": 1}"
                          isRedOn = true
                      }
                     
                        manager.publish(msg, to: customTopic)
                    }.disabled(!manager.isConnected)
                        .background(isRedOn ? Color.red: Color.mint)
                        
                        .controlSize(.large)
                    Spacer()
                    Button("Green"){
                        var msg = "{\"green\": 1}"
                        if isGreenOn {
                            msg = "{\"green\": 0}"
                            isGreenOn = false
                        } else {
                            msg = "{\"green\": 1}"
                            isGreenOn = true
                        }
                        manager.publish(msg, to: customTopic)
                      }.disabled(!manager.isConnected)
                        .background(isGreenOn ? Color.red: Color.mint)
                        
                        .controlSize(.regular)
                    Spacer()
                    Button("Yellow"){
                        var msg = "{\"yellow\": 1}"
                        if isYellowOn {
                            msg = "{\"yellow\": 0}"
                            isYellowOn = false
                        } else {
                            msg = "{\"yellow\": 1}"
                            isYellowOn = true
                        }
                        manager.publish(msg, to: customTopic)
                      }.disabled(!manager.isConnected)
                        .background(isYellowOn ? Color.red: Color.mint)
                        
                        .controlSize(.regular)
                    Spacer()
                }
                HStack(spacing: 15){
                    List(manager.messages, id: \.self) {
                        msg in
                        Text(msg)
                            .font(.system(.caption2, design: .monospaced))
                    }
                    .navigationTitle("MQTT Client")
                }
            }
            .padding()
        }
    }
}

#Preview {
    ContentView()
}








