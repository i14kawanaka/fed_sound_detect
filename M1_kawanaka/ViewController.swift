//
//  ViewController.swift
//  M1_kawanaka
//
//  Created by kawanaka masaki on 2021/10/06.
//

import UIKit
import Alamofire
import Firebase

class ViewController: UIViewController {
    let socketSignal = SocketSignal()
    var PredResult = [String:Any]()
    let texts = ["動物の鳴き声","雨の音","火の音","風の音","波の音","雷雨","人の生活音","PC作業音","生活音","都市の騒音"]
    let text2 = ["1:ほとんど聞こえない","2:ほんの少し聞こえる","3:聞こえる大きさ","4:少し気になる大きさ","5:とてもうるさい"]

    @IBOutlet weak var V1label: UILabel!
    @IBOutlet weak var V2label: UILabel!
    @IBOutlet weak var V1title: UILabel!
    @IBOutlet weak var V2title: UILabel!
    @IBOutlet weak var imageV2: UIImageView!
    @IBOutlet weak var imageV1: UIImageView!
    @IBOutlet weak var get_json: UIButton!
    @IBOutlet weak var Crowdlabel: UILabel!
    @IBOutlet weak var go_second: UIButton!
    var image: UIImage!
    var imageArray = [UIImage]()
    //var image2: UIImage!
    let db = Firestore.firestore()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        socketSignal.ipAddress = "163.221.129.137:5000"
        socketSignal.delegate = self
        //socketSignal.connect()
        
        V1title.text = "最新の識別結果"
        V2title.text = "１つ前の識別結果"
        
        for i in 0..<10{
            print(i)
            let image = UIImage(named: "\(i)")
            imageArray.append(image!)}
        
        //image.image = image1
        // Do any additional setup after loading the view.
    }
    
    @IBAction func get_json(_ sender: Any) {
        //self.request(url: "http://\(self.socketSignal.ipAddress!)")
        //self.addAdaLovelace()
        self.getCollection()
        self.getCrowd()
        //image.image = image2
    }
    
    @IBAction func go_second_board(_ sender: Any) {
        self.performSegue(withIdentifier: "toSubViewController", sender: nil)
    }
    func request(url: String) {
        AF.request(url, method: .get, parameters: nil, encoding: JSONEncoding.default, headers: nil).response { response in
                guard let data = response.data else { return }
                let responseModel: ResponseModel = try! JSONDecoder().decode(ResponseModel.self, from: data)
            self.disp_img(curNum: responseModel.Cur, preNum: responseModel.Pre)
            print(responseModel.Cur)
            }
    }
    
    func disp_img(curNum: Int, preNum: Int) {
        imageV1.image = imageArray[curNum]
        V1label.text = texts[curNum]
        imageV2.image = imageArray[preNum]
        V2label.text = texts[preNum]
        //if(bookNum == 3){
        //    image.image = image2
        //}
    }
    
    func disp_text(croNum: Int){
        Crowdlabel.text = text2[croNum]
    }
    
    private func getCollection() {
            // [START get_collection]
        db.collection("users").getDocuments() { [self] (querySnapshot, err) in
                if let err = err {
                    print("Error getting documents: \(err)")
                } else {
                    for document in querySnapshot!.documents {
                        self.PredResult = document.data()
                        print("\(document.data())")
                        print(PredResult["Cur"]!)
                        self.disp_img(curNum: PredResult["Cur"] as! Int, preNum: PredResult["Pre"] as! Int)
                    }
                }
            }
            // [END get_collection]
        }
    private func getCrowd() {
        db.collection("users2").getDocuments() { [self] (querySnapshot, err) in
                if let err = err {
                    print("Error getting documents: \(err)")
                } else {
                    for document in querySnapshot!.documents {
                        self.PredResult = document.data()
                        print("\(document.data())")
                        self.disp_text(croNum: PredResult["Crowd"] as! Int)
                    }
                }
            }
    }

}



@available(iOS 11.0, *)
extension ViewController: SocketProtcol {
    func aaa() {
        //print("-----4679-0---------------------------")
        //request(url: "http://\(self.socketSignal.ipAddress!)")
        //print("-----4679-0---afafa------------------------")
    }
}

