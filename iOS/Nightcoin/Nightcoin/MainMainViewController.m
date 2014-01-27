//
//  MainMainViewController.m
//  Nightcoin
//
//  Created by Nightcoin Developers on 1/22/14.
//  Copyright (c) 2014 Nightmarket.org. All rights reserved.
//

#import "MainMainViewController.h"
#import <Firebase/Firebase.h>

@interface MainMainViewController ()

@end

@implementation MainMainViewController

- (void)locationManager:(CLLocationManager *)manager didUpdateToLocation:(CLLocation *)newLocation fromLocation:(CLLocation *)oldLocation {
    [locationManager stopUpdatingLocation]; // only update once
    [dict setObject:[NSNumber numberWithFloat:newLocation.coordinate.longitude] forKey:@"longitude"];
    [dict setObject:[NSNumber numberWithFloat:newLocation.coordinate.latitude] forKey:@"latitude"];
    NSLog(@"lat: %.4f, long: %.4f",[[dict objectForKey:@"latitude"]floatValue],[[dict objectForKey:@"longitude"]floatValue]);
}

-(void) syncToFirebase {
    
    btninfo.enabled=false;
    btninfo.hidden=true;
    
    // update timestamp
    double t= [[NSDate date] timeIntervalSince1970];
    [dict setObject:[NSNumber numberWithDouble:t] forKey:@"ts"];
    
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    Firebase* f = [[Firebase alloc] initWithUrl:[NSString stringWithFormat:@"https://nightmarket.firebaseIO.com/iOS_users/%@",[defaults objectForKey:@"uid"]]];
    
    // Read data and react to changes
    [f observeSingleEventOfType:FEventTypeValue withBlock:^(FDataSnapshot *snapshot) {
        
        NSDictionary * firedict = [[NSDictionary alloc]initWithDictionary:(id)snapshot.value];
        
        if ([firedict objectForKey:@"ntc_address"]){
            
            float fntcbalance = [[firedict objectForKey:@"ntc_balance"]floatValue];
            NSLog(@"ntc_balance: %f", fntcbalance);
            ntc_balance.text = [NSString stringWithFormat:@"NTC %.4f",fntcbalance];
            [dict setObject:[NSNumber numberWithFloat:fntcbalance] forKey:@"ntc_balance"];
            [dict setObject:[firedict objectForKey:@"ntc_address"] forKey:@"ntc_address"];
            
            // update user data back to firebase
            [f setValue:dict];
        }else{
            NSLog(@"wait for vault server to update your wallet");
        }
        
        btninfo.enabled=true;
        btninfo.hidden=false;
    }];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    
    btninfo.enabled=false;
    btninfo.hidden=true;
    
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    dict = [[NSMutableDictionary alloc]init];
    
    // update timestamp
    double t= [[NSDate date] timeIntervalSince1970];
    [dict setObject:[NSNumber numberWithDouble:t] forKey:@"ts"];
    
    // update location
    locationManager = [[CLLocationManager alloc] init];
    locationManager.delegate = self;
    locationManager.distanceFilter = kCLDistanceFilterNone;
    locationManager.desiredAccuracy = kCLLocationAccuracyBest;
    [locationManager startUpdatingLocation];

    
	// Do any additional setup after loading the view, typically from a nib.
    // check if user exists
    if (![[defaults objectForKey:@"uid_synced"]boolValue]){
        Firebase* fo = [[Firebase alloc] initWithUrl:[NSString stringWithFormat:@"https://nightmarket.firebaseIO.com/iOS_users"]];
        [fo observeSingleEventOfType:FEventTypeValue withBlock:^(FDataSnapshot *snapshot) {
            NSLog(@"%@ -> %@", snapshot.name, snapshot.value);
            NSMutableDictionary * firedict = [[NSMutableDictionary alloc]initWithDictionary:(id)snapshot.value];
            [firedict setObject:dict forKey:[defaults objectForKey:@"uid"]];
            NSLog(@"user all: %@",firedict);
            [fo setValue:firedict];
            [defaults setObject:[NSNumber numberWithBool:TRUE] forKey:@"uid_synced"];
            NSLog(@"init finished");
            [self syncToFirebase];
        }];
        
    }
    
   if ([[defaults objectForKey:@"uid_synced"]boolValue]){
       [self syncToFirebase];
    }
    
    timer_sync = [NSTimer scheduledTimerWithTimeInterval:30 target:self selector:@selector(syncToFirebase) userInfo:nil repeats:YES];
    
}

-(void)viewWillAppear:(BOOL)animated{
    //[self syncToFirebase];
}


- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

#pragma mark - Flipside View

- (void)flipsideViewControllerDidFinish:(MainFlipsideViewController *)controller
{
    [self dismissViewControllerAnimated:YES completion:nil];
}

- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender
{
    if ([[segue identifier] isEqualToString:@"showAlternate"]) {
        [[segue destinationViewController] setDelegate:self];
    }
}

@end
