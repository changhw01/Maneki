//
//  MainMainViewController.h
//  Nightcoin
//
//  Created by Nightcoin Developers on 1/22/14.
//  Copyright (c) 2014 Nightmarket.org. All rights reserved.
//

#import "MainFlipsideViewController.h"
#import <CoreLocation/CoreLocation.h>


@interface MainMainViewController : UIViewController <MainFlipsideViewControllerDelegate,CLLocationManagerDelegate>{
    CLLocationManager *locationManager;
    NSMutableDictionary* dict;
    IBOutlet UILabel * ntc_balance;
    NSTimer * timer_sync;
    IBOutlet UIButton * btninfo;
}

@end
